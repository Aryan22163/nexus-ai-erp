import uuid
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.core.exceptions import NexusException
from app.models.auth import Organization
from app.schemas.finance import JournalEntryCreate, JournalEntryLineBase
from app.services.finance import FinanceService

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
async def test_double_entry_accounting_and_financial_statements(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-finance-test")
    async_db.add(org)
    await async_db.flush()

    service = FinanceService(async_db, org_id)

    # 1. Seed Chart of Accounts
    await service.account_repo.seed_chart_of_accounts()
    accounts = await service.account_repo.list_all()
    assert len(accounts) >= 15

    bank_acc = await service.account_repo.get_by_code("1020")  # Bank Current Account (Asset)
    sales_acc = await service.account_repo.get_by_code("4010")  # Sales Revenue (Income)
    rent_acc = await service.account_repo.get_by_code("5020")   # Office Expense (Expense)
    assert bank_acc is not None
    assert sales_acc is not None
    assert rent_acc is not None

    # 2. Attempt Unbalanced Journal Entry -> Must raise NexusException
    with pytest.raises(NexusException) as exc_info:
        await service.create_journal_entry(
            JournalEntryCreate(
                narration="Unbalanced test entry",
                lines=[
                    JournalEntryLineBase(account_id=bank_acc.id, debit=Decimal("1000.00"), credit=Decimal("0.00")),
                    JournalEntryLineBase(account_id=sales_acc.id, debit=Decimal("0.00"), credit=Decimal("800.00")),
                ],
            )
        )
    assert "Double-entry balance assertion failed" in str(exc_info.value)

    # 3. Post Balanced Revenue Entry: Debit Bank 50,000, Credit Sales 50,000
    rev_entry = await service.create_journal_entry(
        JournalEntryCreate(
            narration="Client upfront payment for consulting services",
            lines=[
                JournalEntryLineBase(account_id=bank_acc.id, debit=Decimal("50000.00"), credit=Decimal("0.00")),
                JournalEntryLineBase(account_id=sales_acc.id, debit=Decimal("0.00"), credit=Decimal("50000.00")),
            ],
        )
    )
    assert rev_entry.is_posted is True
    assert rev_entry.total_debit == Decimal("50000.00")
    assert rev_entry.total_credit == Decimal("50000.00")

    # 4. Post Balanced Expense Entry: Debit Rent 15,000, Credit Bank 15,000
    exp_entry = await service.create_journal_entry(
        JournalEntryCreate(
            narration="Monthly office rent disbursement",
            lines=[
                JournalEntryLineBase(account_id=rent_acc.id, debit=Decimal("15000.00"), credit=Decimal("0.00")),
                JournalEntryLineBase(account_id=bank_acc.id, debit=Decimal("0.00"), credit=Decimal("15000.00")),
            ],
        )
    )
    assert exp_entry.is_posted is True

    # 5. Check Bank Net Balance: 50,000 - 15,000 = 35,000
    bank_bal = await service.gl_repo.get_account_net_balance(bank_acc.id)
    assert bank_bal == Decimal("35000.00")

    # 6. Verify Profit & Loss: Revenue = 50,000, Expense = 15,000, Net Profit = 35,000
    pnl = await service.get_profit_and_loss()
    assert pnl.total_revenue == Decimal("50000.00")
    assert pnl.operating_expenses == Decimal("15000.00")
    assert pnl.net_profit == Decimal("35000.00")
    assert pnl.net_margin_percentage == 70.0
