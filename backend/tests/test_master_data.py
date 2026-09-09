import uuid
from datetime import date
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.models.auth import Organization
from app.models.organization import (
    Branch,
    Department,
    FiscalYear,
    TaxConfiguration,
    Warehouse,
)
from app.repositories.organization_masters import (
    BranchRepository,
    DepartmentRepository,
    FiscalYearRepository,
    TaxConfigurationRepository,
    WarehouseRepository,
)

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
async def test_organization_branch_and_warehouse(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-retail")
    async_db.add(org)
    await async_db.flush()

    branch_repo = BranchRepository(async_db, org_id)
    warehouse_repo = WarehouseRepository(async_db, org_id)

    # Create Branch
    branch = await branch_repo.create(
        name="Bangalore Flagship Branch",
        code="BLR-01",
        city="Bangalore",
        country="India",
    )
    assert branch.id is not None
    assert branch.organization_id == org_id

    # Create Warehouse attached to branch
    warehouse = await warehouse_repo.create(
        name="Indiranagar Depot",
        code="WH-INDIRA",
        branch_id=branch.id,
    )
    assert warehouse.id is not None
    assert warehouse.organization_id == org_id
    assert warehouse.branch_id == branch.id

    # Lookup warehouse by code
    found_wh = await warehouse_repo.get_by_code("WH-INDIRA")
    assert found_wh is not None
    assert found_wh.name == "Indiranagar Depot"


@pytest.mark.asyncio
async def test_fiscal_year_and_taxes(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-retail-fy")
    async_db.add(org)
    await async_db.flush()

    fy_repo = FiscalYearRepository(async_db, org_id)
    tax_repo = TaxConfigurationRepository(async_db, org_id)

    # Create Fiscal Year
    fy = await fy_repo.create(
        name="FY 2026-27",
        start_date=date(2026, 4, 1),
        end_date=date(2027, 3, 31),
        is_closed=False,
    )
    assert fy.id is not None
    active_fy = await fy_repo.get_active_fiscal_year()
    assert active_fy is not None
    assert active_fy.name == "FY 2026-27"

    # Create Tax Configurations
    tax18 = await tax_repo.create(
        name="Standard GST 18%",
        code="GST-18",
        rate=Decimal("18.00"),
        tax_type="GST",
    )
    tax0 = await tax_repo.create(
        name="Zero Rated",
        code="GST-0",
        rate=Decimal("0.00"),
        tax_type="GST",
    )
    taxes = await tax_repo.list_all()
    assert len(taxes) == 2
    assert {t.code for t in taxes} == {"GST-18", "GST-0"}
