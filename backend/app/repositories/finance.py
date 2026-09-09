import uuid
from decimal import Decimal
from typing import Dict, List, Optional, Sequence, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.finance import Account, CostCenter, GeneralLedger, JournalEntry, JournalEntryLine
from app.repositories.base import BaseTenantRepository

STANDARD_ACCOUNTS = [
    # Assets
    {"code": "1000", "name": "Assets", "type": "ASSET", "is_group": True},
    {"code": "1010", "name": "Cash on Hand", "type": "ASSET", "parent_code": "1000"},
    {"code": "1020", "name": "Bank Current Account", "type": "ASSET", "parent_code": "1000"},
    {"code": "1030", "name": "Accounts Receivable (Debtors)", "type": "ASSET", "parent_code": "1000"},
    {"code": "1040", "name": "Inventory Asset", "type": "ASSET", "parent_code": "1000"},
    # Liabilities
    {"code": "2000", "name": "Liabilities", "type": "LIABILITY", "is_group": True},
    {"code": "2010", "name": "Accounts Payable (Creditors)", "type": "LIABILITY", "parent_code": "2000"},
    {"code": "2020", "name": "GST / Tax Payable", "type": "LIABILITY", "parent_code": "2000"},
    # Equity
    {"code": "3000", "name": "Equity", "type": "EQUITY", "is_group": True},
    {"code": "3010", "name": "Retained Earnings", "type": "EQUITY", "parent_code": "3000"},
    {"code": "3020", "name": "Share Capital", "type": "EQUITY", "parent_code": "3000"},
    # Income
    {"code": "4000", "name": "Income", "type": "INCOME", "is_group": True},
    {"code": "4010", "name": "Sales Revenue", "type": "INCOME", "parent_code": "4000"},
    {"code": "4020", "name": "Other Operating Income", "type": "INCOME", "parent_code": "4000"},
    # Expenses
    {"code": "5000", "name": "Expenses", "type": "EXPENSE", "is_group": True},
    {"code": "5010", "name": "Cost of Goods Sold (COGS)", "type": "EXPENSE", "parent_code": "5000"},
    {"code": "5020", "name": "Office & Administration Expense", "type": "EXPENSE", "parent_code": "5000"},
    {"code": "5030", "name": "Salaries & Employee Benefits", "type": "EXPENSE", "parent_code": "5000"},
    {"code": "5040", "name": "Marketing & Advertising", "type": "EXPENSE", "parent_code": "5000"},
]


class AccountRepository(BaseTenantRepository[Account]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Account, session, organization_id)

    async def get_by_code(self, code: str) -> Optional[Account]:
        stmt = select(Account).where(
            Account.organization_id == self.organization_id,
            Account.account_code == code,
            Account.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def seed_chart_of_accounts(self) -> None:
        """Seed the standard 5-pillar Chart of Accounts for a new organization."""
        existing = {acc.account_code: acc for acc in await self.list_all()}
        if existing:
            return

        code_to_acc: Dict[str, Account] = {}

        # 1. Create root groups
        for defn in STANDARD_ACCOUNTS:
            if defn.get("is_group"):
                acc = Account(
                    organization_id=self.organization_id,
                    account_code=defn["code"],
                    name=defn["name"],
                    account_type=defn["type"],
                    is_group=True,
                )
                self.session.add(acc)
                code_to_acc[defn["code"]] = acc

        await self.session.flush()

        # 2. Create child accounts
        for defn in STANDARD_ACCOUNTS:
            if not defn.get("is_group"):
                parent = code_to_acc.get(defn.get("parent_code"))
                acc = Account(
                    organization_id=self.organization_id,
                    account_code=defn["code"],
                    name=defn["name"],
                    account_type=defn["type"],
                    parent_id=parent.id if parent else None,
                    is_group=False,
                )
                self.session.add(acc)

        await self.session.flush()


class JournalEntryRepository(BaseTenantRepository[JournalEntry]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(JournalEntry, session, organization_id)

    async def get_with_lines(self, entry_id: uuid.UUID) -> Optional[JournalEntry]:
        stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines).selectinload(JournalEntryLine.account))
            .where(
                JournalEntry.id == entry_id,
                JournalEntry.organization_id == self.organization_id,
                JournalEntry.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class GeneralLedgerRepository(BaseTenantRepository[GeneralLedger]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(GeneralLedger, session, organization_id)

    async def get_account_net_balance(self, account_id: uuid.UUID) -> Decimal:
        """Calculate net balance = Sum(debits) - Sum(credits)."""
        stmt = (
            select(
                func.coalesce(func.sum(GeneralLedger.debit), 0).label("total_debit"),
                func.coalesce(func.sum(GeneralLedger.credit), 0).label("total_credit"),
            )
            .where(
                GeneralLedger.organization_id == self.organization_id,
                GeneralLedger.account_id == account_id,
                GeneralLedger.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if row:
            return Decimal(str(row.total_debit)) - Decimal(str(row.total_credit))
        return Decimal("0.00")

    async def get_total_by_account_type(self, account_type: str) -> Decimal:
        """Sum total activity for a specific root account type."""
        stmt = (
            select(
                func.coalesce(func.sum(GeneralLedger.debit), 0).label("total_debit"),
                func.coalesce(func.sum(GeneralLedger.credit), 0).label("total_credit"),
            )
            .join(Account, Account.id == GeneralLedger.account_id)
            .where(
                GeneralLedger.organization_id == self.organization_id,
                Account.account_type == account_type.upper(),
                GeneralLedger.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if not row:
            return Decimal("0.00")

        total_deb = Decimal(str(row.total_debit))
        total_cred = Decimal(str(row.total_credit))

        # Assets & Expenses are normal debit balance: Debit - Credit
        if account_type.upper() in ["ASSET", "EXPENSE"]:
            return total_deb - total_cred
        # Liabilities, Equity, Income are normal credit balance: Credit - Debit
        return total_cred - total_deb
