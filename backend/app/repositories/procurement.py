import uuid
from typing import List, Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.procurement import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseReceipt,
    PurchaseRequest,
    PurchaseRequestItem,
    Supplier,
)
from app.repositories.base import BaseTenantRepository


class SupplierRepository(BaseTenantRepository[Supplier]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Supplier, session, organization_id)

    async def get_by_name(self, name: str) -> Optional[Supplier]:
        stmt = select(Supplier).where(
            Supplier.organization_id == self.organization_id,
            Supplier.name == name,
            Supplier.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PurchaseRequestRepository(BaseTenantRepository[PurchaseRequest]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(PurchaseRequest, session, organization_id)

    async def get_with_items(self, request_id: uuid.UUID) -> Optional[PurchaseRequest]:
        stmt = (
            select(PurchaseRequest)
            .options(selectinload(PurchaseRequest.items))
            .where(
                PurchaseRequest.id == request_id,
                PurchaseRequest.organization_id == self.organization_id,
                PurchaseRequest.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PurchaseOrderRepository(BaseTenantRepository[PurchaseOrder]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(PurchaseOrder, session, organization_id)

    async def get_with_items(self, order_id: uuid.UUID) -> Optional[PurchaseOrder]:
        stmt = (
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .where(
                PurchaseOrder.id == order_id,
                PurchaseOrder.organization_id == self.organization_id,
                PurchaseOrder.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PurchaseReceiptRepository(BaseTenantRepository[PurchaseReceipt]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(PurchaseReceipt, session, organization_id)
