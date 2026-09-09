import uuid
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.core.exceptions import NexusException
from app.models.auth import Organization
from app.models.organization import Warehouse
from app.models.sales import Product
from app.schemas.inventory import StockEntryCreate, StockEntryItemBase
from app.services.inventory import InventoryService

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
async def test_inventory_ledger_receipt_and_transfer(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-inv-test")
    async_db.add(org)
    await async_db.flush()

    service = InventoryService(async_db, org_id)

    # 1. Setup Warehouses and Product
    wh1 = Warehouse(organization_id=org_id, name="Central WH", code="WH-CENTRAL")
    wh2 = Warehouse(organization_id=org_id, name="Outlet WH", code="WH-OUTLET")
    product = Product(
        organization_id=org_id,
        sku="SKU-CHIP-99",
        name="SoC Processor Unit",
        standard_selling_price=Decimal("5000.00"),
        standard_cost_price=Decimal("3000.00"),
        reorder_level=Decimal("20.00"),
        reorder_quantity=Decimal("100.00"),
    )
    async_db.add_all([wh1, wh2, product])
    await async_db.flush()

    # 2. Material Receipt of 100 units @ 3000 each into Central WH
    receipt_entry = await service.create_stock_entry(
        StockEntryCreate(
            entry_type="MATERIAL_RECEIPT",
            to_warehouse_id=wh1.id,
            items=[
                StockEntryItemBase(
                    product_id=product.id,
                    quantity=Decimal("100.00"),
                    unit_cost=Decimal("3000.00"),
                    batch_number="BATCH-2026-A1",
                )
            ],
        )
    )
    assert receipt_entry.id is not None
    qty, val = await service.ledger_repo.get_latest_product_balance(product.id, wh1.id)
    assert qty == Decimal("100.00")
    assert val == Decimal("300000.00")

    # 3. Transfer 30 units from Central WH to Outlet WH
    transfer_entry = await service.create_stock_entry(
        StockEntryCreate(
            entry_type="MATERIAL_TRANSFER",
            from_warehouse_id=wh1.id,
            to_warehouse_id=wh2.id,
            items=[
                StockEntryItemBase(
                    product_id=product.id,
                    quantity=Decimal("30.00"),
                    unit_cost=Decimal("3000.00"),
                )
            ],
        )
    )
    assert transfer_entry.id is not None

    # Check Central WH has 70 remaining
    wh1_qty, wh1_val = await service.ledger_repo.get_latest_product_balance(product.id, wh1.id)
    assert wh1_qty == Decimal("70.00")
    assert wh1_val == Decimal("210000.00")

    # Check Outlet WH has 30
    wh2_qty, wh2_val = await service.ledger_repo.get_latest_product_balance(product.id, wh2.id)
    assert wh2_qty == Decimal("30.00")
    assert wh2_val == Decimal("90000.00")

    # 4. Attempt to overdraw: transfer 80 units from Central WH (only 70 available) -> Must raise NexusException
    with pytest.raises(NexusException) as exc_info:
        await service.create_stock_entry(
            StockEntryCreate(
                entry_type="MATERIAL_ISSUE",
                from_warehouse_id=wh1.id,
                items=[
                    StockEntryItemBase(
                        product_id=product.id,
                        quantity=Decimal("80.00"),
                        unit_cost=Decimal("3000.00"),
                    )
                ],
            )
        )
    assert "Insufficient stock" in str(exc_info.value)


@pytest.mark.asyncio
async def test_low_stock_proactive_alert(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-lowstock-test")
    async_db.add(org)
    await async_db.flush()

    service = InventoryService(async_db, org_id)

    # Product with reorder_level = 15, current stock = 0
    product = Product(
        organization_id=org_id,
        sku="SKU-VALVE-01",
        name="Hydraulic Solenoid Valve",
        reorder_level=Decimal("15.00"),
        reorder_quantity=Decimal("50.00"),
        is_stock_item=True,
    )
    async_db.add(product)
    await async_db.flush()

    # Trigger alert check
    alerts = await service.get_low_stock_alerts()
    assert len(alerts) == 1
    assert alerts[0].sku == "SKU-VALVE-01"
    assert alerts[0].current_stock == Decimal("0.00")
    assert alerts[0].urgency == "CRITICAL"
    assert alerts[0].recommended_reorder_qty == Decimal("50.00")
