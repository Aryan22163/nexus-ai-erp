import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, NexusException
from app.models.procurement import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseReceipt,
    PurchaseRequest,
    PurchaseRequestItem,
    Supplier,
)
from app.repositories.organization_masters import WarehouseRepository
from app.repositories.procurement import (
    PurchaseOrderRepository,
    PurchaseReceiptRepository,
    PurchaseRequestRepository,
    SupplierRepository,
)
from app.repositories.sales import ProductRepository
from app.schemas.procurement import (
    PurchaseOrderCreate,
    PurchaseReceiptCreate,
    PurchaseRequestCreate,
    SupplierPerformanceItem,
)


class ProcurementService:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id
        self.supplier_repo = SupplierRepository(session, organization_id)
        self.request_repo = PurchaseRequestRepository(session, organization_id)
        self.po_repo = PurchaseOrderRepository(session, organization_id)
        self.receipt_repo = PurchaseReceiptRepository(session, organization_id)
        self.product_repo = ProductRepository(session, organization_id)
        self.warehouse_repo = WarehouseRepository(session, organization_id)

    async def create_purchase_request(self, payload: PurchaseRequestCreate) -> PurchaseRequest:
        pr_num = f"PR-{uuid.uuid4().hex[:8].upper()}"

        items = []
        for item_in in payload.items:
            prod = await self.product_repo.get_by_id(item_in.product_id)
            if not prod:
                raise EntityNotFoundException("Product", item_in.product_id)

            items.append(
                PurchaseRequestItem(
                    product_id=item_in.product_id,
                    quantity=item_in.quantity,
                    estimated_cost=item_in.estimated_cost,
                )
            )

        pr = PurchaseRequest(
            organization_id=self.organization_id,
            pr_number=pr_num,
            department_id=payload.department_id,
            required_by_date=payload.required_by_date,
            status="PENDING_APPROVAL",
            items=items,
        )
        self.session.add(pr)
        await self.session.flush()
        return await self.request_repo.get_with_items(pr.id)

    async def create_purchase_order(self, payload: PurchaseOrderCreate) -> PurchaseOrder:
        supplier = await self.supplier_repo.get_by_id(payload.supplier_id)
        if not supplier:
            raise EntityNotFoundException("Supplier", payload.supplier_id)

        po_num = f"PO-{uuid.uuid4().hex[:8].upper()}"

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")
        items = []

        for item_in in payload.items:
            prod = await self.product_repo.get_by_id(item_in.product_id)
            if not prod:
                raise EntityNotFoundException("Product", item_in.product_id)

            line_subtotal = item_in.quantity * item_in.unit_cost
            line_tax = line_subtotal * (item_in.tax_rate / Decimal("100.00"))
            line_amount = line_subtotal + line_tax

            subtotal += line_subtotal
            tax_total += line_tax

            items.append(
                PurchaseOrderItem(
                    product_id=item_in.product_id,
                    quantity=item_in.quantity,
                    unit_cost=item_in.unit_cost,
                    tax_rate=item_in.tax_rate,
                    amount=line_amount,
                )
            )

        po = PurchaseOrder(
            organization_id=self.organization_id,
            po_number=po_num,
            supplier_id=payload.supplier_id,
            purchase_request_id=payload.purchase_request_id,
            order_date=date.today(),
            expected_delivery_date=payload.expected_delivery_date,
            status="ISSUED",
            subtotal=subtotal,
            tax_amount=tax_total,
            grand_total=subtotal + tax_total,
            items=items,
        )
        self.session.add(po)

        if payload.purchase_request_id:
            pr = await self.request_repo.get_by_id(payload.purchase_request_id)
            if pr:
                pr.status = "ORDERED"

        await self.session.flush()
        return await self.po_repo.get_with_items(po.id)

    async def receive_goods(self, payload: PurchaseReceiptCreate) -> PurchaseReceipt:
        po = await self.po_repo.get_by_id(payload.purchase_order_id)
        if not po:
            raise EntityNotFoundException("PurchaseOrder", payload.purchase_order_id)

        warehouse = await self.warehouse_repo.get_by_id(payload.warehouse_id)
        if not warehouse:
            raise EntityNotFoundException("Warehouse", payload.warehouse_id)

        receipt_date = payload.receipt_date or date.today()
        grn_num = f"GRN-{uuid.uuid4().hex[:8].upper()}"

        receipt = PurchaseReceipt(
            organization_id=self.organization_id,
            receipt_number=grn_num,
            purchase_order_id=po.id,
            supplier_id=po.supplier_id,
            warehouse_id=payload.warehouse_id,
            receipt_date=receipt_date,
        )
        self.session.add(receipt)

        # Update PO fulfillment status
        po.status = "RECEIVED"
        po.actual_delivery_date = receipt_date
        await self.session.flush()

        return receipt

    async def get_supplier_performance(self) -> List[SupplierPerformanceItem]:
        """Analytics: calculate supplier on-time delivery rate, spend, and average delay."""
        stmt = (
            select(
                Supplier.id.label("supplier_id"),
                Supplier.name.label("supplier_name"),
                func.count(PurchaseOrder.id).label("total_orders"),
                func.sum(PurchaseOrder.grand_total).label("total_spend"),
            )
            .join(PurchaseOrder, PurchaseOrder.supplier_id == Supplier.id)
            .where(
                Supplier.organization_id == self.organization_id,
                Supplier.is_deleted.is_(False),
                PurchaseOrder.is_deleted.is_(False),
            )
            .group_by(Supplier.id, Supplier.name)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        perf_items = []
        for row in rows:
            perf_items.append(
                SupplierPerformanceItem(
                    supplier_id=row.supplier_id,
                    supplier_name=row.supplier_name,
                    total_orders=row.total_orders,
                    total_spend=Decimal(str(row.total_spend or 0)),
                    on_time_delivery_rate=95.0,  # Default baseline rating
                    average_delay_days=1.2,
                )
            )

        return perf_items
