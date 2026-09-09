import uuid
from decimal import Decimal
from typing import List, Optional, Sequence, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.inventory import StockEntry, StockEntryItem, StockLedger
from app.models.organization import Warehouse
from app.models.sales import Product
from app.repositories.base import BaseTenantRepository


class StockEntryRepository(BaseTenantRepository[StockEntry]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(StockEntry, session, organization_id)

    async def get_with_items(self, entry_id: uuid.UUID) -> Optional[StockEntry]:
        stmt = (
            select(StockEntry)
            .options(selectinload(StockEntry.items))
            .where(
                StockEntry.id == entry_id,
                StockEntry.organization_id == self.organization_id,
                StockEntry.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class StockLedgerRepository(BaseTenantRepository[StockLedger]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(StockLedger, session, organization_id)

    async def get_latest_product_balance(
        self, product_id: uuid.UUID, warehouse_id: uuid.UUID
    ) -> Tuple[Decimal, Decimal]:
        """Fetch the most recent balance_quantity and balance_value for a product in a warehouse."""
        stmt = (
            select(StockLedger.balance_quantity, StockLedger.balance_value)
            .where(
                StockLedger.organization_id == self.organization_id,
                StockLedger.product_id == product_id,
                StockLedger.warehouse_id == warehouse_id,
                StockLedger.is_deleted.is_(False),
            )
            .order_by(StockLedger.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if row:
            return Decimal(str(row.balance_quantity)), Decimal(str(row.balance_value))
        return Decimal("0.00"), Decimal("0.00")

    async def get_stock_balance_summary(self) -> Sequence[dict]:
        """Aggregate current stock levels across all products and warehouses."""
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.sku.label("sku"),
                Product.name.label("product_name"),
                Warehouse.id.label("warehouse_id"),
                Warehouse.name.label("warehouse_name"),
                func.sum(StockLedger.quantity_delta).label("current_quantity"),
                func.sum(StockLedger.balance_value).label("balance_value"),
                func.avg(StockLedger.valuation_rate).label("avg_valuation_rate"),
            )
            .join(Product, Product.id == StockLedger.product_id)
            .join(Warehouse, Warehouse.id == StockLedger.warehouse_id)
            .where(
                StockLedger.organization_id == self.organization_id,
                StockLedger.is_deleted.is_(False),
            )
            .group_by(Product.id, Product.sku, Product.name, Warehouse.id, Warehouse.name)
            .having(func.sum(StockLedger.quantity_delta) > 0)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "product_id": row.product_id,
                "sku": row.sku,
                "product_name": row.product_name,
                "warehouse_id": row.warehouse_id,
                "warehouse_name": row.warehouse_name,
                "current_quantity": Decimal(str(row.current_quantity or 0)),
                "valuation_rate": Decimal(str(row.avg_valuation_rate or 0)),
                "total_value": Decimal(str(row.current_quantity or 0)) * Decimal(str(row.avg_valuation_rate or 0)),
            }
            for row in rows
        ]
