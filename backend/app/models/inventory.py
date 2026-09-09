import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import IdMixin, TenantBaseModel
from app.models.organization import Warehouse
from app.models.sales import Product


class ProductBatch(TenantBaseModel):
    """Batch/Lot number tracking for perishable or batch-controlled products."""
    __tablename__ = "product_batches"

    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    manufacturing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    product: Mapped["Product"] = relationship("Product")


class ProductSerial(TenantBaseModel):
    """Unique serial number tracking for individual high-value items."""
    __tablename__ = "product_serials"

    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False,
    )  # ACTIVE, SOLD, RETURNED, DEFECTIVE

    product: Mapped["Product"] = relationship("Product")
    warehouse: Mapped[Optional["Warehouse"]] = relationship("Warehouse")


class StockEntry(TenantBaseModel):
    """Header record for internal material movements, transfers, or adjustments."""
    __tablename__ = "stock_entries"

    entry_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entry_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # MATERIAL_RECEIPT, MATERIAL_ISSUE, MATERIAL_TRANSFER, STOCK_ADJUSTMENT
    from_warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=True,
    )
    to_warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=True,
    )
    posting_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    items: Mapped[List["StockEntryItem"]] = relationship(
        "StockEntryItem",
        back_populates="entry",
        cascade="all, delete-orphan",
    )


class StockEntryItem(Base, IdMixin):
    __tablename__ = "stock_entry_items"

    stock_entry_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("stock_entries.id", ondelete="CASCADE"),
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
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    entry: Mapped["StockEntry"] = relationship("StockEntry", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class StockLedger(TenantBaseModel):
    """
    Immutable audit ledger of physical inventory movements.
    Every inventory state change generates immutable ledger entries.
    """
    __tablename__ = "stock_ledger"

    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    voucher_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # PURCHASE_RECEIPT, DELIVERY_NOTE, STOCK_ENTRY, STOCK_ADJUSTMENT
    voucher_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    quantity_delta: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)  # + for inbound, - for outbound
    valuation_rate: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    balance_quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    balance_value: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    posting_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    product: Mapped["Product"] = relationship("Product")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse")
