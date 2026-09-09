import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, NexusException
from app.models.inventory import StockEntry, StockEntryItem, StockLedger
from app.models.sales import Product
from app.repositories.inventory import StockEntryRepository, StockLedgerRepository
from app.repositories.organization_masters import WarehouseRepository
from app.repositories.sales import ProductRepository
from app.schemas.inventory import (
    LowStockAlertItem,
    StockBalanceItem,
    StockEntryCreate,
)


class InventoryService:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id
        self.entry_repo = StockEntryRepository(session, organization_id)
        self.ledger_repo = StockLedgerRepository(session, organization_id)
        self.product_repo = ProductRepository(session, organization_id)
        self.warehouse_repo = WarehouseRepository(session, organization_id)

    async def create_stock_entry(self, payload: StockEntryCreate) -> StockEntry:
        """Process an inventory movement and append immutable audit records to the Stock Ledger."""
        entry_num = f"STE-{uuid.uuid4().hex[:8].upper()}"
        posting_dt = payload.posting_date or date.today()

        entry = StockEntry(
            organization_id=self.organization_id,
            entry_number=entry_num,
            entry_type=payload.entry_type,
            from_warehouse_id=payload.from_warehouse_id,
            to_warehouse_id=payload.to_warehouse_id,
            posting_date=posting_dt,
            remarks=payload.remarks,
        )
        self.session.add(entry)
        await self.session.flush()

        for item_in in payload.items:
            product = await self.product_repo.get_by_id(item_in.product_id)
            if not product:
                raise EntityNotFoundException("Product", item_in.product_id)

            entry_item = StockEntryItem(
                stock_entry_id=entry.id,
                product_id=item_in.product_id,
                quantity=item_in.quantity,
                unit_cost=item_in.unit_cost,
                batch_number=item_in.batch_number,
                serial_number=item_in.serial_number,
            )
            self.session.add(entry_item)

            # Inbound / Receipt / Transfer In
            if payload.to_warehouse_id:
                curr_qty, curr_val = await self.ledger_repo.get_latest_product_balance(
                    item_in.product_id, payload.to_warehouse_id
                )
                new_qty = curr_qty + item_in.quantity
                new_val = curr_val + (item_in.quantity * item_in.unit_cost)
                new_rate = (new_val / new_qty) if new_qty > 0 else item_in.unit_cost

                ledger_in = StockLedger(
                    organization_id=self.organization_id,
                    product_id=item_in.product_id,
                    warehouse_id=payload.to_warehouse_id,
                    voucher_type="STOCK_ENTRY",
                    voucher_id=entry.id,
                    quantity_delta=item_in.quantity,
                    valuation_rate=new_rate,
                    balance_quantity=new_qty,
                    balance_value=new_val,
                    batch_number=item_in.batch_number,
                    serial_number=item_in.serial_number,
                    posting_date=posting_dt,
                )
                self.session.add(ledger_in)

            # Outbound / Issue / Transfer Out
            if payload.from_warehouse_id:
                curr_qty, curr_val = await self.ledger_repo.get_latest_product_balance(
                    item_in.product_id, payload.from_warehouse_id
                )
                if curr_qty < item_in.quantity:
                    raise NexusException(
                        f"Insufficient stock for {product.name} (SKU: {product.sku}) in source warehouse. "
                        f"Available: {curr_qty}, Requested: {item_in.quantity}"
                    )

                valuation_rate = (curr_val / curr_qty) if curr_qty > 0 else item_in.unit_cost
                new_qty = curr_qty - item_in.quantity
                new_val = max(Decimal("0.00"), curr_val - (item_in.quantity * valuation_rate))

                ledger_out = StockLedger(
                    organization_id=self.organization_id,
                    product_id=item_in.product_id,
                    warehouse_id=payload.from_warehouse_id,
                    voucher_type="STOCK_ENTRY",
                    voucher_id=entry.id,
                    quantity_delta=-item_in.quantity,
                    valuation_rate=valuation_rate,
                    balance_quantity=new_qty,
                    balance_value=new_val,
                    batch_number=item_in.batch_number,
                    serial_number=item_in.serial_number,
                    posting_date=posting_dt,
                )
                self.session.add(ledger_out)

        await self.session.flush()
        return await self.entry_repo.get_with_items(entry.id)

    async def get_stock_balance(self) -> List[StockBalanceItem]:
        summary_rows = await self.ledger_repo.get_stock_balance_summary()
        return [StockBalanceItem(**row) for row in summary_rows]

    async def get_low_stock_alerts(self) -> List[LowStockAlertItem]:
        """Proactive AI low-stock and stockout projection tool."""
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.sku.label("sku"),
                Product.name.label("product_name"),
                Product.reorder_level.label("reorder_level"),
                Product.reorder_quantity.label("reorder_qty"),
                func.coalesce(func.sum(StockLedger.quantity_delta), 0).label("current_stock"),
            )
            .outerjoin(StockLedger, (StockLedger.product_id == Product.id) & (StockLedger.is_deleted.is_(False)))
            .where(
                Product.organization_id == self.organization_id,
                Product.is_stock_item.is_(True),
                Product.is_deleted.is_(False),
            )
            .group_by(Product.id, Product.sku, Product.name, Product.reorder_level, Product.reorder_quantity)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        alerts = []
        for row in rows:
            curr_stock = Decimal(str(row.current_stock or 0))
            reorder_lvl = Decimal(str(row.reorder_level or 10))
            reorder_qty = Decimal(str(row.reorder_qty or 50))

            if curr_stock <= reorder_lvl:
                urgency = "CRITICAL" if curr_stock <= (reorder_lvl / 2) else "WARNING"
                # Simple velocity assumption: 2 units per day
                est_days = max(1, int(curr_stock / 2)) if curr_stock > 0 else 0

                alerts.append(
                    LowStockAlertItem(
                        product_id=row.product_id,
                        sku=row.sku,
                        product_name=row.product_name,
                        current_stock=curr_stock,
                        reorder_level=reorder_lvl,
                        days_until_stockout=est_days,
                        recommended_reorder_qty=reorder_qty,
                        urgency=urgency,
                    )
                )

        return alerts
