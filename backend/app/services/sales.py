import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, NexusException
from app.models.crm import Customer
from app.models.sales import (
    Payment,
    Product,
    Quotation,
    QuotationItem,
    SalesInvoice,
    SalesOrder,
    SalesOrderItem,
)
from app.repositories.crm import CustomerRepository
from app.repositories.sales import (
    PaymentRepository,
    ProductRepository,
    QuotationRepository,
    SalesInvoiceRepository,
    SalesOrderRepository,
)
from app.schemas.sales import (
    PaymentCreate,
    ProductSalesPerformanceItem,
    QuotationCreate,
    SalesInvoiceCreate,
    SalesOrderCreate,
    TopCustomerRevenueItem,
)


class SalesService:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id
        self.product_repo = ProductRepository(session, organization_id)
        self.quotation_repo = QuotationRepository(session, organization_id)
        self.order_repo = SalesOrderRepository(session, organization_id)
        self.invoice_repo = SalesInvoiceRepository(session, organization_id)
        self.payment_repo = PaymentRepository(session, organization_id)
        self.customer_repo = CustomerRepository(session, organization_id)

    async def create_quotation(self, payload: QuotationCreate) -> Quotation:
        customer = await self.customer_repo.get_by_id(payload.customer_id)
        if not customer:
            raise EntityNotFoundException("Customer", payload.customer_id)

        quotation_num = f"QT-{uuid.uuid4().hex[:8].upper()}"

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")
        items = []

        for item_in in payload.items:
            product = await self.product_repo.get_by_id(item_in.product_id)
            if not product:
                raise EntityNotFoundException("Product", item_in.product_id)

            line_subtotal = item_in.quantity * item_in.unit_price
            line_tax = line_subtotal * (item_in.tax_rate / Decimal("100.00"))
            line_amount = line_subtotal + line_tax

            subtotal += line_subtotal
            tax_total += line_tax

            items.append(
                QuotationItem(
                    product_id=item_in.product_id,
                    quantity=item_in.quantity,
                    unit_price=item_in.unit_price,
                    tax_rate=item_in.tax_rate,
                    amount=line_amount,
                )
            )

        quotation = Quotation(
            organization_id=self.organization_id,
            quotation_number=quotation_num,
            customer_id=payload.customer_id,
            valid_until=payload.valid_until,
            status="DRAFT",
            subtotal=subtotal,
            tax_amount=tax_total,
            grand_total=subtotal + tax_total,
            items=items,
        )
        self.session.add(quotation)
        await self.session.flush()
        return await self.quotation_repo.get_with_items(quotation.id)

    async def create_sales_order(self, payload: SalesOrderCreate) -> SalesOrder:
        customer = await self.customer_repo.get_by_id(payload.customer_id)
        if not customer:
            raise EntityNotFoundException("Customer", payload.customer_id)

        order_num = f"SO-{uuid.uuid4().hex[:8].upper()}"

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")
        items = []

        for item_in in payload.items:
            product = await self.product_repo.get_by_id(item_in.product_id)
            if not product:
                raise EntityNotFoundException("Product", item_in.product_id)

            line_subtotal = item_in.quantity * item_in.unit_price
            line_tax = line_subtotal * (item_in.tax_rate / Decimal("100.00"))
            line_amount = line_subtotal + line_tax

            subtotal += line_subtotal
            tax_total += line_tax

            items.append(
                SalesOrderItem(
                    product_id=item_in.product_id,
                    quantity=item_in.quantity,
                    unit_price=item_in.unit_price,
                    tax_rate=item_in.tax_rate,
                    amount=line_amount,
                )
            )

        order = SalesOrder(
            organization_id=self.organization_id,
            order_number=order_num,
            customer_id=payload.customer_id,
            quotation_id=payload.quotation_id,
            delivery_date=payload.delivery_date,
            status="CONFIRMED",
            subtotal=subtotal,
            tax_amount=tax_total,
            grand_total=subtotal + tax_total,
            items=items,
        )
        self.session.add(order)
        await self.session.flush()
        return await self.order_repo.get_with_items(order.id)

    async def create_invoice_from_order(self, payload: SalesInvoiceCreate) -> SalesInvoice:
        order = await self.order_repo.get_with_items(payload.sales_order_id)
        if not order:
            raise EntityNotFoundException("SalesOrder", payload.sales_order_id)

        inv_num = f"INV-{uuid.uuid4().hex[:8].upper()}"

        invoice = SalesInvoice(
            organization_id=self.organization_id,
            invoice_number=inv_num,
            customer_id=order.customer_id,
            sales_order_id=order.id,
            due_date=payload.due_date,
            status="UNPAID",
            total_amount=order.grand_total,
            paid_amount=Decimal("0.00"),
            outstanding_amount=order.grand_total,
        )
        self.session.add(invoice)
        await self.session.flush()
        return invoice

    async def record_payment(self, payload: PaymentCreate) -> Payment:
        invoice = await self.invoice_repo.get_by_id(payload.invoice_id)
        if not invoice:
            raise EntityNotFoundException("SalesInvoice", payload.invoice_id)

        if invoice.outstanding_amount <= Decimal("0.00"):
            raise NexusException("Invoice is already fully settled.")

        pay_num = f"PAY-{uuid.uuid4().hex[:8].upper()}"

        payment = Payment(
            organization_id=self.organization_id,
            payment_number=pay_num,
            invoice_id=invoice.id,
            customer_id=invoice.customer_id,
            payment_date=date.today(),
            amount=payload.amount,
            payment_method=payload.payment_method,
            reference_number=payload.reference_number,
        )
        self.session.add(payment)

        # Update invoice balance
        invoice.paid_amount += payload.amount
        invoice.outstanding_amount = max(Decimal("0.00"), invoice.total_amount - invoice.paid_amount)

        if invoice.outstanding_amount == Decimal("0.00"):
            invoice.status = "PAID"
        else:
            invoice.status = "PARTIALLY_PAID"

        await self.session.flush()
        return payment

    async def get_top_customers(self, limit: int = 10) -> List[TopCustomerRevenueItem]:
        """Analytics query: Rank top customers by confirmed sales revenue."""
        stmt = (
            select(
                Customer.id.label("customer_id"),
                Customer.name.label("customer_name"),
                func.sum(SalesOrder.grand_total).label("total_revenue"),
                func.count(SalesOrder.id).label("orders_count"),
            )
            .join(SalesOrder, SalesOrder.customer_id == Customer.id)
            .where(
                Customer.organization_id == self.organization_id,
                SalesOrder.status.in_(["CONFIRMED", "FULFILLED"]),
                Customer.is_deleted.is_(False),
                SalesOrder.is_deleted.is_(False),
            )
            .group_by(Customer.id, Customer.name)
            .order_by(func.sum(SalesOrder.grand_total).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            TopCustomerRevenueItem(
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                total_revenue=Decimal(str(row.total_revenue or 0)),
                orders_count=row.orders_count,
            )
            for row in rows
        ]

    async def get_product_sales_performance(self, limit: int = 15) -> List[ProductSalesPerformanceItem]:
        """Analytics query: Evaluate sales velocity and revenue by product SKU."""
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.sku.label("sku"),
                Product.name.label("product_name"),
                func.sum(SalesOrderItem.quantity).label("units_sold"),
                func.sum(SalesOrderItem.amount).label("total_revenue"),
            )
            .join(SalesOrderItem, SalesOrderItem.product_id == Product.id)
            .join(SalesOrder, SalesOrder.id == SalesOrderItem.sales_order_id)
            .where(
                Product.organization_id == self.organization_id,
                SalesOrder.status.in_(["CONFIRMED", "FULFILLED"]),
                Product.is_deleted.is_(False),
                SalesOrder.is_deleted.is_(False),
            )
            .group_by(Product.id, Product.sku, Product.name)
            .order_by(func.sum(SalesOrderItem.amount).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            ProductSalesPerformanceItem(
                product_id=row.product_id,
                sku=row.sku,
                product_name=row.product_name,
                units_sold=Decimal(str(row.units_sold or 0)),
                total_revenue=Decimal(str(row.total_revenue or 0)),
            )
            for row in rows
        ]
