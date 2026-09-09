import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Account Schemas ---
class AccountBase(BaseModel):
    account_code: str = Field(..., examples=["1010"])
    name: str = Field(..., examples=["Bank Account - HDFC"])
    account_type: str = Field(..., examples=["ASSET"])  # ASSET, LIABILITY, EQUITY, INCOME, EXPENSE
    parent_id: Optional[uuid.UUID] = None
    is_group: bool = False
    is_active: bool = True


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Journal Entry Line Schemas ---
class JournalEntryLineBase(BaseModel):
    account_id: uuid.UUID
    debit: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit: Decimal = Field(default=Decimal("0.00"), ge=0)
    cost_center_id: Optional[uuid.UUID] = None
    user_remark: Optional[str] = None


class JournalEntryLineResponse(JournalEntryLineBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- Journal Entry Schemas ---
class JournalEntryCreate(BaseModel):
    posting_date: Optional[date] = None
    narration: str = Field(..., examples=["Office rent payment for September 2026"])
    reference_type: str = Field(default="MANUAL")
    reference_id: Optional[uuid.UUID] = None
    lines: List[JournalEntryLineBase] = Field(..., min_length=2)


class JournalEntryResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    entry_number: str
    posting_date: date
    narration: str
    total_debit: Decimal
    total_credit: Decimal
    is_posted: bool
    lines: List[JournalEntryLineResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Financial Statements ---
class ProfitAndLossReport(BaseModel):
    total_revenue: Decimal
    cost_of_goods_sold: Decimal
    gross_profit: Decimal
    operating_expenses: Decimal
    net_profit: Decimal
    net_margin_percentage: float


class BalanceSheetReport(BaseModel):
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    is_balanced: bool  # Assets == Liabilities + Equity


class AccountsReceivableAging(BaseModel):
    current: Decimal
    days_1_to_30: Decimal
    days_31_to_60: Decimal
    over_60_days: Decimal
    total_outstanding: Decimal
