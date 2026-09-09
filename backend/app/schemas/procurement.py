import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Supplier Schemas ---
class SupplierBase(BaseModel):
    name: str = Field(..., examples=["Foxconn Electronics India"])
    contact_name: Optional[str] = Field(None, examples=["Ming Zhao"])
    email: Optional[EmailStr] = Field(None, examples=["b2b@foxconn.com"])
    phone: Optional[str] = Field(None, examples=["+91 44 2715 0000"])
    address: Optional[dict[str, Any]] = None
    payment_terms: str = Field(default="NET30", examples=["NET30"])
    rating: float = Field(default=5.0, ge=1.0, le=5.0)
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Purchase Request Schemas ---
class PurchaseRequestItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0, examples=[Decimal("100.00")])
    estimated_cost: Decimal = Field(..., gt=0, examples=[Decimal("2500.00")])


class PurchaseRequestCreate(BaseModel):
    required_by_date: date
    department_id: Optional[uuid.UUID] = None
    items: List[PurchaseRequestItemBase] = Field(..., min_length=1)


class PurchaseRequestResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    pr_number: str
    required_by_date: date
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Purchase Order Schemas ---
class PurchaseOrderItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0, examples=[Decimal("100.00")])
    unit_cost: Decimal = Field(..., gt=0, examples=[Decimal("2450.00")])
    tax_rate: Decimal = Field(default=Decimal("18.00"))


class PurchaseOrderCreate(BaseModel):
    supplier_id: uuid.UUID
    purchase_request_id: Optional[uuid.UUID] = None
    expected_delivery_date: date
    items: List[PurchaseOrderItemBase] = Field(..., min_length=1)


class PurchaseOrderResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    po_number: str
    supplier_id: uuid.UUID
    order_date: date
    expected_delivery_date: date
    actual_delivery_date: Optional[date] = None
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    grand_total: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Purchase Receipt Schemas ---
class PurchaseReceiptCreate(BaseModel):
    purchase_order_id: uuid.UUID
    warehouse_id: uuid.UUID
    receipt_date: Optional[date] = None


class PurchaseReceiptResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    receipt_number: str
    purchase_order_id: uuid.UUID
    supplier_id: uuid.UUID
    warehouse_id: uuid.UUID
    receipt_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Supplier Performance Analytics ---
class SupplierPerformanceItem(BaseModel):
    supplier_id: uuid.UUID
    supplier_name: str
    total_orders: int
    total_spend: Decimal
    on_time_delivery_rate: float
    average_delay_days: float
