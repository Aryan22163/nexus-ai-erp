import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Product Schemas ---
class ProductCategoryBase(BaseModel):
    name: str = Field(..., examples=["Industrial Electronics"])
    code: str = Field(..., examples=["CAT-ELEC"])
    description: Optional[str] = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryResponse(ProductCategoryBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    sku: str = Field(..., examples=["SKU-ELEC-001"])
    name: str = Field(..., examples=["High-Precision Temperature Sensor"])
    category_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    uom: str = Field(default="NOS", examples=["NOS"])
    standard_selling_price: Decimal = Field(..., examples=[Decimal("4500.00")])
    standard_cost_price: Decimal = Field(..., examples=[Decimal("2800.00")])
    reorder_level: Decimal = Field(default=Decimal("10.00"))
    reorder_quantity: Decimal = Field(default=Decimal("50.00"))
    is_stock_item: bool = True
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Item Line Schemas ---
class OrderItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0, examples=[Decimal("10.00")])
    unit_price: Decimal = Field(..., gt=0, examples=[Decimal("4500.00")])
    tax_rate: Decimal = Field(default=Decimal("18.00"))


class OrderItemResponse(OrderItemBase):
    id: uuid.UUID
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


# --- Quotation Schemas ---
class QuotationCreate(BaseModel):
    customer_id: uuid.UUID
    valid_until: date
    items: List[OrderItemBase] = Field(..., min_length=1)


class QuotationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    quotation_number: str
    customer_id: uuid.UUID
    valid_until: date
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    grand_total: Decimal
    items: List[OrderItemResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Sales Order Schemas ---
class SalesOrderCreate(BaseModel):
    customer_id: uuid.UUID
    quotation_id: Optional[uuid.UUID] = None
    delivery_date: Optional[date] = None
    items: List[OrderItemBase] = Field(..., min_length=1)


class SalesOrderResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    order_number: str
    customer_id: uuid.UUID
    order_date: date
    delivery_date: Optional[date] = None
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    grand_total: Decimal
    items: List[OrderItemResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Sales Invoice Schemas ---
class SalesInvoiceCreate(BaseModel):
    sales_order_id: uuid.UUID
    due_date: date


class SalesInvoiceResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    invoice_number: str
    customer_id: uuid.UUID
    sales_order_id: Optional[uuid.UUID] = None
    issue_date: date
    due_date: date
    status: str
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Payment Schemas ---
class PaymentCreate(BaseModel):
    invoice_id: uuid.UUID
    amount: Decimal = Field(..., gt=0, examples=[Decimal("25000.00")])
    payment_method: str = Field(default="BANK_TRANSFER", examples=["BANK_TRANSFER"])
    reference_number: Optional[str] = Field(None, examples=["NEFT-UTR-99882233"])


class PaymentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    payment_number: str
    invoice_id: uuid.UUID
    customer_id: uuid.UUID
    payment_date: date
    amount: Decimal
    payment_method: str
    reference_number: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Sales Analytics Query Responses ---
class TopCustomerRevenueItem(BaseModel):
    customer_id: uuid.UUID
    customer_name: str
    total_revenue: Decimal
    orders_count: int


class ProductSalesPerformanceItem(BaseModel):
    product_id: uuid.UUID
    sku: str
    product_name: str
    units_sold: Decimal
    total_revenue: Decimal
