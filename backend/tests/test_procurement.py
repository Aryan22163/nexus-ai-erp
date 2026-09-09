import uuid
from datetime import date, timedelta
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.models.auth import Organization
from app.models.organization import Warehouse
from app.models.procurement import Supplier
from app.models.sales import Product
from app.schemas.procurement import (
    PurchaseOrderCreate,
    PurchaseOrderItemBase,
    PurchaseReceiptCreate,
    PurchaseRequestCreate,
    PurchaseRequestItemBase,
)
from app.services.procurement import ProcurementService

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
async def test_procurement_request_to_receipt_lifecycle(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-procure-test")
    async_db.add(org)
    await async_db.flush()

    service = ProcurementService(async_db, org_id)

    # 1. Setup supplier, product, warehouse
    supplier = Supplier(
        organization_id=org_id,
        name="Foxconn Precision Components",
        email="orders@foxconn.com",
        payment_terms="NET30",
    )
    product = Product(
        organization_id=org_id,
        sku="SKU-MICRO-01",
        name="ARM Cortex M4 Processor",
        standard_selling_price=Decimal("1200.00"),
        standard_cost_price=Decimal("650.00"),
    )
    warehouse = Warehouse(
        organization_id=org_id,
        name="Main Electronic Storage WH",
        code="WH-ELEC-01",
    )
    async_db.add_all([supplier, product, warehouse])
    await async_db.flush()

    # 2. Create Purchase Request
    pr = await service.create_purchase_request(
        PurchaseRequestCreate(
            required_by_date=date.today() + timedelta(days=14),
            items=[
                PurchaseRequestItemBase(
                    product_id=product.id,
                    quantity=Decimal("500.00"),
                    estimated_cost=Decimal("650.00"),
                )
            ],
        )
    )
    assert pr.status == "PENDING_APPROVAL"
    assert len(pr.items) == 1

    # 3. Create Purchase Order linked to PR
    po = await service.create_purchase_order(
        PurchaseOrderCreate(
            supplier_id=supplier.id,
            purchase_request_id=pr.id,
            expected_delivery_date=date.today() + timedelta(days=10),
            items=[
                PurchaseOrderItemBase(
                    product_id=product.id,
                    quantity=Decimal("500.00"),
                    unit_cost=Decimal("640.00"),  # negotiated discount
                    tax_rate=Decimal("18.00"),
                )
            ],
        )
    )
    # 500 * 640 = 320,000 subtotal, 57,600 tax = 377,600 grand total
    assert po.status == "ISSUED"
    assert po.subtotal == Decimal("320000.00")
    assert po.tax_amount == Decimal("57600.00")
    assert po.grand_total == Decimal("377600.00")

    # Verify PR status transitioned to ORDERED
    pr_check = await service.request_repo.get_by_id(pr.id)
    assert pr_check.status == "ORDERED"

    # 4. Receive Goods (GRN)
    receipt = await service.receive_goods(
        PurchaseReceiptCreate(
            purchase_order_id=po.id,
            warehouse_id=warehouse.id,
        )
    )
    assert receipt.id is not None
    assert receipt.receipt_number.startswith("GRN-")

    # Verify PO status transitioned to RECEIVED
    po_check = await service.po_repo.get_by_id(po.id)
    assert po_check.status == "RECEIVED"
    assert po_check.actual_delivery_date == date.today()

    # 5. Supplier Performance Analytics
    perf = await service.get_supplier_performance()
    assert len(perf) == 1
    assert perf[0].supplier_name == "Foxconn Precision Components"
    assert perf[0].total_orders == 1
    assert perf[0].total_spend == Decimal("377600.00")
