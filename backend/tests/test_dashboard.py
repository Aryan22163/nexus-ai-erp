import uuid
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.models.auth import Organization
from app.models.crm import Customer
from app.models.organization import Warehouse
from app.models.sales import Product
from app.schemas.finance import JournalEntryCreate, JournalEntryLineBase
from app.schemas.inventory import StockEntryCreate, StockEntryItemBase
from app.services.dashboard import DashboardService
from app.services.finance import FinanceService
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
async def test_executive_dashboard_summary_aggregation(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-dash-test")
    async_db.add(org)
    await async_db.flush()

    dash_service = DashboardService(async_db, org_id)
    finance_service = FinanceService(async_db, org_id)
    inv_service = InventoryService(async_db, org_id)

    # 1. Seed Finance Chart of Accounts & post revenue
    await finance_service.account_repo.seed_chart_of_accounts()
    bank = await finance_service.account_repo.get_by_code("1020")
    sales = await finance_service.account_repo.get_by_code("4010")

    await finance_service.create_journal_entry(
        JournalEntryCreate(
            narration="Sales Q3 Revenue",
            lines=[
                JournalEntryLineBase(account_id=bank.id, debit=Decimal("100000.00"), credit=Decimal("0.00")),
                JournalEntryLineBase(account_id=sales.id, debit=Decimal("0.00"), credit=Decimal("100000.00")),
            ],
        )
    )

    # 2. Add customer with high churn risk
    at_risk_cust = Customer(
        organization_id=org_id,
        name="Losing Account Corp",
        churn_risk_score=0.85,
    )
    async_db.add(at_risk_cust)

    # 3. Add warehouse and low-stock product
    wh = Warehouse(organization_id=org_id, name="Depot WH", code="WH-DEPOT")
    product = Product(
        organization_id=org_id,
        sku="SKU-ALERT-1",
        name="Critical Semiconductor",
        reorder_level=Decimal("20.00"),
        is_stock_item=True,
    )
    async_db.add_all([wh, product])
    await async_db.flush()

    # 4. Fetch Executive Summary
    summary = await dash_service.get_executive_summary()
    assert summary is not None
    assert len(summary.kpis) == 4

    # Verify Revenue KPI
    rev_kpi = next(k for k in summary.kpis if k.title == "Total Revenue")
    assert rev_kpi.numeric_value == Decimal("100000.00")

    # Verify Proactive AI Insights
    insight_titles = [i.title for i in summary.ai_insights]
    assert "Customer Churn Risk Alert" in insight_titles
    assert "Inventory Stockout Forecast" in insight_titles
    assert summary.total_active_customers == 1
    assert summary.low_stock_items_count == 1
