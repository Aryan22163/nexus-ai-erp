import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import AuditMixin, IdMixin, SoftDeleteMixin, TenantBaseModel


class Branch(TenantBaseModel):
    """Physical branch or operating office belonging to an organization."""
    __tablename__ = "branches"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    warehouses: Mapped[List["Warehouse"]] = relationship("Warehouse", back_populates="branch")


class Department(TenantBaseModel):
    """Organizational department with hierarchical parent support."""
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    children: Mapped[List["Department"]] = relationship(
        "Department",
        backref="parent",
        remote_side="Department.id",
    )


class BusinessUnit(TenantBaseModel):
    """Cost center or distinct strategic business unit (SBU)."""
    __tablename__ = "business_units"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Warehouse(TenantBaseModel):
    """Storage location for stock and inventory."""
    __tablename__ = "warehouses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    branch: Mapped[Optional["Branch"]] = relationship("Branch", back_populates="warehouses")


class FiscalYear(TenantBaseModel):
    """Accounting fiscal financial period."""
    __tablename__ = "fiscal_years"

    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "FY 2026-27"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class CurrencyExchangeRate(TenantBaseModel):
    """Currency conversion rate relative to organization's base currency."""
    __tablename__ = "currency_exchange_rates"

    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)


class TaxConfiguration(TenantBaseModel):
    """Tax templates (GST, VAT, Sales Tax) applied across sales and procurement."""
    __tablename__ = "tax_configurations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "GST 18%", "Zero Rated"
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)  # e.g., 18.00
    tax_type: Mapped[str] = mapped_column(String(50), default="GST", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
