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


class ProductCategory(TenantBaseModel):
    """Catalog classification for products and services."""
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")


class Product(TenantBaseModel):
    """Item or service sold or procured in business operations."""
    __tablename__ = "products"

    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("product_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uom: Mapped[str] = mapped_column(String(20), default="NOS", nullable=False)  # Unit of Measure (NOS, KG, MTR, BOX)
    standard_selling_price: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    standard_cost_price: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    reorder_level: Mapped[float] = mapped_column(Numeric(12, 2), default=10.00, nullable=False)
    reorder_quantity: Mapped[float] = mapped_column(Numeric(12, 2), default=50.00, nullable=False)
    is_stock_item: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory", back_populates="products")


class PriceList(TenantBaseModel):
    """Configurable customer or tiered price lists."""
    __tablename__ = "price_lists"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    items: Mapped[List["PriceListItem"]] = relationship(
        "PriceListItem",
        back_populates="price_list",
        cascade="all, delete-orphan",
    )


class PriceListItem(Base, IdMixin):
    """Individual item rate under a Price List."""
    __tablename__ = "price_list_items"

    price_list_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("price_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rate: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    price_list: Mapped["PriceList"] = relationship("PriceList", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class Quotation(TenantBaseModel):
    """Formal commercial quotation submitted to a customer."""
    __tablename__ = "quotations"

    quotation_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False)  # DRAFT, SENT, ACCEPTED, DECLINED, EXPIRED
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    grand_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)

    items: Mapped[List["QuotationItem"]] = relationship(
        "QuotationItem",
        back_populates="quotation",
        cascade="all, delete-orphan",
    )


class QuotationItem(Base, IdMixin):
    __tablename__ = "quotation_items"

    quotation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("quotations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=18.00, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class SalesOrder(TenantBaseModel):
    """Confirmed sales contract with delivery commitments."""
    __tablename__ = "sales_orders"

    order_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quotation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("quotations.id", ondelete="SET NULL"),
        nullable=True,
    )
    order_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False)  # DRAFT, CONFIRMED, FULFILLED, CANCELLED
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    grand_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)

    items: Mapped[List["SalesOrderItem"]] = relationship(
        "SalesOrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    invoices: Mapped[List["SalesInvoice"]] = relationship("SalesInvoice", back_populates="sales_order")


class SalesOrderItem(Base, IdMixin):
    __tablename__ = "sales_order_items"

    sales_order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sales_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=18.00, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class SalesInvoice(TenantBaseModel):
    """Tax invoice billed to customer."""
    __tablename__ = "sales_invoices"

    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sales_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sales_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    issue_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="UNPAID", nullable=False)  # UNPAID, PARTIALLY_PAID, PAID, OVERDUE, CANCELLED
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    outstanding_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    sales_order: Mapped[Optional["SalesOrder"]] = relationship("SalesOrder", back_populates="invoices")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="invoice")


class Payment(TenantBaseModel):
    """Payment received against customer invoices."""
    __tablename__ = "payments"

    payment_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sales_invoices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payment_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="BANK_TRANSFER", nullable=False)  # BANK_TRANSFER, UPI, CREDIT_CARD, CASH
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    invoice: Mapped["SalesInvoice"] = relationship("SalesInvoice", back_populates="payments")
