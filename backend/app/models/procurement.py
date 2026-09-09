import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Date,
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
from app.models.base import IdMixin, TenantBaseModel
from app.models.sales import Product


class Supplier(TenantBaseModel):
    """Vendor or raw material / component supplier."""
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    payment_terms: Mapped[str] = mapped_column(String(50), default="NET30", nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)  # 1.0 to 5.0
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="supplier")


class PurchaseRequest(TenantBaseModel):
    """Internal requisition for materials or services."""
    __tablename__ = "purchase_requests"

    pr_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    requested_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    required_by_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="DRAFT",
        nullable=False,
    )  # DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, ORDERED

    items: Mapped[List["PurchaseRequestItem"]] = relationship(
        "PurchaseRequestItem",
        back_populates="request",
        cascade="all, delete-orphan",
    )


class PurchaseRequestItem(Base, IdMixin):
    __tablename__ = "purchase_request_items"

    request_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("purchase_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    request: Mapped["PurchaseRequest"] = relationship("PurchaseRequest", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class PurchaseOrder(TenantBaseModel):
    """Commercial contract issued to a supplier."""
    __tablename__ = "purchase_orders"

    po_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    purchase_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("purchase_requests.id", ondelete="SET NULL"),
        nullable=True,
    )
    order_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    expected_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="DRAFT",
        nullable=False,
    )  # DRAFT, ISSUED, RECEIVED, BILLED, CANCELLED
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    grand_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="purchase_orders")
    items: Mapped[List["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    receipts: Mapped[List["PurchaseReceipt"]] = relationship("PurchaseReceipt", back_populates="purchase_order")


class PurchaseOrderItem(Base, IdMixin):
    __tablename__ = "purchase_order_items"

    purchase_order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=18.00, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class PurchaseReceipt(TenantBaseModel):
    """Goods Receipt Note (GRN) acknowledging physical delivery at warehouse."""
    __tablename__ = "purchase_receipts"

    receipt_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("purchase_orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
    )
    receipt_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="receipts")
