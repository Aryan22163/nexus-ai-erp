import uuid
from datetime import date, timedelta
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.models.auth import Organization
from app.models.crm import Customer
from app.models.sales import Product
from app.schemas.sales import (
    OrderItemBase,
    PaymentCreate,
    QuotationCreate,
    SalesInvoiceCreate,
    SalesOrderCreate,
)
from app.services.sales import SalesService

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_full_sales_order_to_payment_lifecycle(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-sales-test")
    async_db.add(org)
    await async_db.flush()

    service = SalesService(async_db, org_id)

    # 1. Create a customer
    customer = Customer(
        organization_id=org_id,
        name="Reliance Retail Ltd",
        email="purchase@relianceretail.com",
        customer_segment="ENTERPRISE",
    )
    async_db.add(customer)

    # 2. Create products
    p1 = Product(
        organization_id=org_id,
        sku="SKU-POS-01",
        name="Android POS Terminal",
        standard_selling_price=Decimal("10000.00"),
        standard_cost_price=Decimal("6500.00"),
    )
    p2 = Product(
        organization_id=org_id,
        sku="SKU-SCAN-02",
        name="Barcode Scanner",
        standard_selling_price=Decimal("2000.00"),
        standard_cost_price=Decimal("1100.00"),
    )
    async_db.add_all([p1, p2])
    await async_db.flush()

    # 3. Create Quotation (2x POS @ 10,000 + 18% tax = 23,600)
    quote = await service.create_quotation(
        QuotationCreate(
            customer_id=customer.id,
            valid_until=date.today() + timedelta(days=30),
            items=[
                OrderItemBase(
                    product_id=p1.id,
                    quantity=Decimal("2.00"),
                    unit_price=Decimal("10000.00"),
                    tax_rate=Decimal("18.00"),
                )
            ],
        )
    )
    assert quote.subtotal == Decimal("20000.00")
    assert quote.tax_amount == Decimal("3600.00")
    assert quote.grand_total == Decimal("23600.00")

    # 4. Create Sales Order from Quotation
    order = await service.create_sales_order(
        SalesOrderCreate(
            customer_id=customer.id,
            quotation_id=quote.id,
            items=[
                OrderItemBase(
                    product_id=p1.id,
                    quantity=Decimal("2.00"),
                    unit_price=Decimal("10000.00"),
                    tax_rate=Decimal("18.00"),
                ),
                OrderItemBase(
                    product_id=p2.id,
                    quantity=Decimal("5.00"),
                    unit_price=Decimal("2000.00"),
                    tax_rate=Decimal("18.00"),
                ),
            ],
        )
    )
    # 20,000 + 10,000 = 30,000 subtotal, 5,400 tax = 35,400 grand total
    assert order.subtotal == Decimal("30000.00")
    assert order.tax_amount == Decimal("5400.00")
    assert order.grand_total == Decimal("35400.00")

    # 5. Generate Invoice
    invoice = await service.create_invoice_from_order(
        SalesInvoiceCreate(
            sales_order_id=order.id,
            due_date=date.today() + timedelta(days=15),
        )
    )
    assert invoice.status == "UNPAID"
    assert invoice.total_amount == Decimal("35400.00")
    assert invoice.outstanding_amount == Decimal("35400.00")

    # 6. Record Partial Payment of 20,000
    payment_part = await service.record_payment(
        PaymentCreate(
            invoice_id=invoice.id,
            amount=Decimal("20000.00"),
            payment_method="BANK_TRANSFER",
            reference_number="NEFT-TXN-101",
        )
    )
    assert invoice.status == "PARTIALLY_PAID"
    assert invoice.paid_amount == Decimal("20000.00")
    assert invoice.outstanding_amount == Decimal("15400.00")

    # 7. Settle Remaining Payment of 15,400
    payment_final = await service.record_payment(
        PaymentCreate(
            invoice_id=invoice.id,
            amount=Decimal("15400.00"),
            payment_method="UPI",
            reference_number="UPI-REF-202",
        )
    )
    assert invoice.status == "PAID"
    assert invoice.outstanding_amount == Decimal("0.00")

    # 8. Test Analytics: Top Customers
    top_custs = await service.get_top_customers()
    assert len(top_custs) == 1
    assert top_custs[0].customer_name == "Reliance Retail Ltd"
    assert top_custs[0].total_revenue == Decimal("35400.00")

    # 9. Test Analytics: Product Performance
    prod_perf = await service.get_product_sales_performance()
    assert len(prod_perf) == 2
    # Highest revenue product is POS Terminal (23,600)
    assert prod_perf[0].sku == "SKU-POS-01"
    assert prod_perf[0].units_sold == Decimal("2.00")
