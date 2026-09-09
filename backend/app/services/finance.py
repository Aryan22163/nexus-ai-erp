import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, NexusException
from app.models.finance import Account, GeneralLedger, JournalEntry, JournalEntryLine
from app.models.sales import SalesInvoice
from app.repositories.finance import (
    AccountRepository,
    GeneralLedgerRepository,
    JournalEntryRepository,
)
from app.schemas.finance import (
    AccountsReceivableAging,
    BalanceSheetReport,
    JournalEntryCreate,
    ProfitAndLossReport,
)


class FinanceService:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id
        self.account_repo = AccountRepository(session, organization_id)
        self.je_repo = JournalEntryRepository(session, organization_id)
        self.gl_repo = GeneralLedgerRepository(session, organization_id)

    async def create_journal_entry(self, payload: JournalEntryCreate) -> JournalEntry:
        """Create and post a balanced double-entry Journal Entry."""
        total_debit = sum(line.debit for line in payload.lines)
        total_credit = sum(line.credit for line in payload.lines)

        if total_debit != total_credit:
            raise NexusException(
                f"Double-entry balance assertion failed! Total Debit (₹{total_debit:,.2f}) "
                f"must equal Total Credit (₹{total_credit:,.2f})."
            )

        if total_debit <= Decimal("0.00"):
            raise NexusException("Total transaction value must be greater than zero.")

        entry_num = f"JV-{uuid.uuid4().hex[:8].upper()}"
        posting_dt = payload.posting_date or date.today()

        entry = JournalEntry(
            organization_id=self.organization_id,
            entry_number=entry_num,
            posting_date=posting_dt,
            reference_type=payload.reference_type,
            reference_id=payload.reference_id,
            narration=payload.narration,
            total_debit=total_debit,
            total_credit=total_credit,
            is_posted=True,
        )
        self.session.add(entry)
        await self.session.flush()

        for line_in in payload.lines:
            acc = await self.account_repo.get_by_id(line_in.account_id)
            if not acc:
                raise EntityNotFoundException("Account", line_in.account_id)
            if acc.is_group:
                raise NexusException(f"Cannot post directly to group account '{acc.name}' (Code: {acc.account_code}).")

            line = JournalEntryLine(
                journal_entry_id=entry.id,
                account_id=line_in.account_id,
                cost_center_id=line_in.cost_center_id,
                debit=line_in.debit,
                credit=line_in.credit,
                user_remark=line_in.user_remark,
            )
            self.session.add(line)

            # Post to immutable General Ledger
            gl_entry = GeneralLedger(
                organization_id=self.organization_id,
                posting_date=posting_dt,
                account_id=line_in.account_id,
                voucher_type="JOURNAL_ENTRY",
                voucher_id=entry.id,
                debit=line_in.debit,
                credit=line_in.credit,
            )
            self.session.add(gl_entry)

        await self.session.flush()
        return await self.je_repo.get_with_lines(entry.id)

    async def get_profit_and_loss(self) -> ProfitAndLossReport:
        """Compute the dynamic Income Statement (P&L)."""
        sales_acc = await self.account_repo.get_by_code("4010")
        cogs_acc = await self.account_repo.get_by_code("5010")

        total_rev = await self.gl_repo.get_total_by_account_type("INCOME")
        cogs = await self.gl_repo.get_account_net_balance(cogs_acc.id) if cogs_acc else Decimal("0.00")
        total_exp = await self.gl_repo.get_total_by_account_type("EXPENSE")

        gross_profit = total_rev - cogs
        net_profit = total_rev - total_exp
        margin = float((net_profit / total_rev) * 100) if total_rev > Decimal("0.00") else 0.0

        return ProfitAndLossReport(
            total_revenue=total_rev,
            cost_of_goods_sold=cogs,
            gross_profit=gross_profit,
            operating_expenses=total_exp - cogs,
            net_profit=net_profit,
            net_margin_percentage=round(margin, 2),
        )

    async def get_balance_sheet(self) -> BalanceSheetReport:
        """Compute Balance Sheet: Total Assets = Total Liabilities + Total Equity."""
        assets = await self.gl_repo.get_total_by_account_type("ASSET")
        liabilities = await self.gl_repo.get_total_by_account_type("LIABILITY")
        equity = await self.gl_repo.get_total_by_account_type("EQUITY")

        return BalanceSheetReport(
            total_assets=assets,
            total_liabilities=liabilities,
            total_equity=equity,
            is_balanced=(assets == (liabilities + equity)),
        )

    async def get_receivables_aging(self) -> AccountsReceivableAging:
        """Accounts Receivable (AR) Aging schedule."""
        stmt = select(SalesInvoice).where(
            SalesInvoice.organization_id == self.organization_id,
            SalesInvoice.outstanding_amount > 0,
            SalesInvoice.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        invoices = result.scalars().all()

        today = date.today()
        curr = Decimal("0.00")
        days1_30 = Decimal("0.00")
        days31_60 = Decimal("0.00")
        over60 = Decimal("0.00")

        for inv in invoices:
            overdue_days = (today - inv.due_date).days
            bal = Decimal(str(inv.outstanding_amount))

            if overdue_days <= 0:
                curr += bal
            elif 1 <= overdue_days <= 30:
                days1_30 += bal
            elif 31 <= overdue_days <= 60:
                days31_60 += bal
            else:
                over60 += bal

        return AccountsReceivableAging(
            current=curr,
            days_1_to_30=days1_30,
            days_31_to_60=days31_60,
            over_60_days=over60,
            total_outstanding=curr + days1_30 + days31_60 + over60,
        )
