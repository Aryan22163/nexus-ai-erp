import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import IdMixin, TenantBaseModel


class Account(TenantBaseModel):
    """Chart of Accounts ledger node (Double-entry accounting structure)."""
    __tablename__ = "accounts"

    account_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    account_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # ASSET, LIABILITY, EQUITY, INCOME, EXPENSE
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=True,
    )
    is_group: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    children: Mapped[List["Account"]] = relationship("Account", backref="parent", remote_side="Account.id")


class CostCenter(TenantBaseModel):
    """Cost allocation center for departmental or project expenditure."""
    __tablename__ = "cost_centers"

    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class JournalEntry(TenantBaseModel):
    """Balanced double-entry journal transaction."""
    __tablename__ = "journal_entries"

    entry_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    posting_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False, index=True)
    reference_type: Mapped[str] = mapped_column(
        String(50),
        default="MANUAL",
        nullable=False,
    )  # MANUAL, SALES_INVOICE, PURCHASE_INVOICE, PAYMENT
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), nullable=True)
    narration: Mapped[str] = mapped_column(Text, nullable=False)
    total_debit: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    total_credit: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    is_posted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    lines: Mapped[List["JournalEntryLine"]] = relationship(
        "JournalEntryLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )


class JournalEntryLine(Base, IdMixin):
    """Individual debit/credit line item."""
    __tablename__ = "journal_entry_lines"

    journal_entry_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cost_center_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cost_centers.id", ondelete="SET NULL"),
        nullable=True,
    )
    debit: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    credit: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    user_remark: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["Account"] = relationship("Account")
    cost_center: Mapped[Optional["CostCenter"]] = relationship("CostCenter")


class GeneralLedger(TenantBaseModel):
    """Immutable denormalized General Ledger for high-throughput reporting."""
    __tablename__ = "general_ledger"

    posting_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    voucher_type: Mapped[str] = mapped_column(String(50), nullable=False)
    voucher_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    debit: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    credit: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)

    account: Mapped["Account"] = relationship("Account")
