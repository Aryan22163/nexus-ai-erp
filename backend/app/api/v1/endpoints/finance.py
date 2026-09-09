from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.repositories.finance import AccountRepository, JournalEntryRepository
from app.schemas.finance import (
    AccountCreate,
    AccountResponse,
    AccountsReceivableAging,
    BalanceSheetReport,
    JournalEntryCreate,
    JournalEntryResponse,
    ProfitAndLossReport,
)
from app.services.finance import FinanceService

router = APIRouter(prefix="/finance", tags=["Finance & Accounting"])


# --- Chart of Accounts ---
@router.get(
    "/accounts",
    response_model=List[AccountResponse],
    dependencies=[Depends(RequirePermissions("finance.read"))],
)
async def list_accounts(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[AccountResponse]:
    repo = AccountRepository(db, tenant.id)
    accounts = await repo.list_all()
    return [AccountResponse.model_validate(a) for a in accounts]


@router.post(
    "/accounts/seed",
    response_model=List[AccountResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("finance.approve"))],
)
async def seed_chart_of_accounts(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[AccountResponse]:
    """Seed the standard 5-pillar Chart of Accounts for the organization."""
    repo = AccountRepository(db, tenant.id)
    await repo.seed_chart_of_accounts()
    accounts = await repo.list_all()
    return [AccountResponse.model_validate(a) for a in accounts]


# --- Journal Entries ---
@router.get(
    "/journal-entries",
    response_model=List[JournalEntryResponse],
    dependencies=[Depends(RequirePermissions("finance.read"))],
)
async def list_journal_entries(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[JournalEntryResponse]:
    repo = JournalEntryRepository(db, tenant.id)
    entries = await repo.list_all()
    return [JournalEntryResponse.model_validate(e) for e in entries]


@router.post(
    "/journal-entries",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("finance.create"))],
)
async def create_journal_entry(
    payload: JournalEntryCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> JournalEntryResponse:
    service = FinanceService(db, tenant.id)
    entry = await service.create_journal_entry(payload)
    return JournalEntryResponse.model_validate(entry)


# --- Financial Statements ---
@router.get(
    "/reports/profit-and-loss",
    response_model=ProfitAndLossReport,
    dependencies=[Depends(RequirePermissions("finance.read"))],
)
async def get_profit_and_loss(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfitAndLossReport:
    service = FinanceService(db, tenant.id)
    return await service.get_profit_and_loss()


@router.get(
    "/reports/balance-sheet",
    response_model=BalanceSheetReport,
    dependencies=[Depends(RequirePermissions("finance.read"))],
)
async def get_balance_sheet(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> BalanceSheetReport:
    service = FinanceService(db, tenant.id)
    return await service.get_balance_sheet()


@router.get(
    "/reports/ar-aging",
    response_model=AccountsReceivableAging,
    dependencies=[Depends(RequirePermissions("finance.read"))],
)
async def get_receivables_aging(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AccountsReceivableAging:
    service = FinanceService(db, tenant.id)
    return await service.get_receivables_aging()
