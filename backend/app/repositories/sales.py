import uuid
from typing import List, Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.crm import Customer
from app.models.sales import (
    Payment,
    Product,
    ProductCategory,
    Quotation,
    QuotationItem,
    SalesInvoice,
    SalesOrder,
    SalesOrderItem,
)
from app.repositories.base import BaseTenantRepository


class ProductRepository(BaseTenantRepository[Product]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Product, session, organization_id)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        stmt = select(Product).where(
            Product.organization_id == self.organization_id,
            Product.sku == sku.upper(),
            Product.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class QuotationRepository(BaseTenantRepository[Quotation]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Quotation, session, organization_id)

    async def get_with_items(self, quotation_id: uuid.UUID) -> Optional[Quotation]:
        stmt = (
            select(Quotation)
            .options(selectinload(Quotation.items))
            .where(
                Quotation.id == quotation_id,
                Quotation.organization_id == self.organization_id,
                Quotation.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class SalesOrderRepository(BaseTenantRepository[SalesOrder]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(SalesOrder, session, organization_id)

    async def get_with_items(self, order_id: uuid.UUID) -> Optional[SalesOrder]:
        stmt = (
            select(SalesOrder)
            .options(selectinload(SalesOrder.items))
            .where(
                SalesOrder.id == order_id,
                SalesOrder.organization_id == self.organization_id,
                SalesOrder.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class SalesInvoiceRepository(BaseTenantRepository[SalesInvoice]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(SalesInvoice, session, organization_id)

    async def get_with_payments(self, invoice_id: uuid.UUID) -> Optional[SalesInvoice]:
        stmt = (
            select(SalesInvoice)
            .options(selectinload(SalesInvoice.payments))
            .where(
                SalesInvoice.id == invoice_id,
                SalesInvoice.organization_id == self.organization_id,
                SalesInvoice.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PaymentRepository(BaseTenantRepository[Payment]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Payment, session, organization_id)
