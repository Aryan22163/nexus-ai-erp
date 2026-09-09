import uuid
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TenantBaseModel


class Customer(TenantBaseModel):
    """Customer account profile."""
    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tax_identifier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # GSTIN, VAT, EIN
    billing_address: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    shipping_address: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    credit_limit: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    customer_segment: Mapped[str] = mapped_column(String(50), default="SMB", nullable=False)  # SMB, ENTERPRISE, STRATEGIC
    churn_risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0.0 - 1.0 ML score
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    contacts: Mapped[List["Contact"]] = relationship(
        "Contact",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    opportunities: Mapped[List["Opportunity"]] = relationship(
        "Opportunity",
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Contact(TenantBaseModel):
    """Individual stakeholder or contact person at a Customer."""
    __tablename__ = "contacts"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="contacts")


class Lead(TenantBaseModel):
    """Sales prospect before customer qualification."""
    __tablename__ = "leads"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="WEBSITE", nullable=False)  # WEBSITE, REFERRAL, EVENT, OUTBOUND
    status: Mapped[str] = mapped_column(String(50), default="NEW", nullable=False)  # NEW, CONTACTED, QUALIFIED, UNQUALIFIED, CONVERTED
    score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)  # 0.0 - 100.0 AI Lead Scoring
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    converted_customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )


class Opportunity(TenantBaseModel):
    """Pipeline deal tracking stage, potential deal size, and close likelihood."""
    __tablename__ = "opportunities"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[str] = mapped_column(
        String(50),
        default="PROSPECTING",
        nullable=False,
        index=True,
    )  # PROSPECTING, QUALIFICATION, PROPOSAL, NEGOTIATION, CLOSED_WON, CLOSED_LOST
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    probability: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)  # 0 - 100%
    expected_close_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="opportunities")


class Activity(TenantBaseModel):
    """Timeline event (Call, Meeting, Note, Follow-up) for Leads, Customers, or Opportunities."""
    __tablename__ = "activities"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # LEAD, CUSTOMER, OPPORTUNITY
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CALL, MEETING, NOTE, FOLLOW_UP
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
