import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Stock Entry Line ---
class StockEntryItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0, examples=[Decimal("50.00")])
    unit_cost: Decimal = Field(..., gt=0, examples=[Decimal("650.00")])
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None


class StockEntryItemResponse(StockEntryItemBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- Stock Entry Header ---
class StockEntryCreate(BaseModel):
    entry_type: str = Field(..., examples=["MATERIAL_RECEIPT"])  # MATERIAL_RECEIPT, MATERIAL_ISSUE, MATERIAL_TRANSFER, STOCK_ADJUSTMENT
    from_warehouse_id: Optional[uuid.UUID] = None
    to_warehouse_id: Optional[uuid.UUID] = None
    posting_date: Optional[date] = None
    remarks: Optional[str] = None
    items: List[StockEntryItemBase] = Field(..., min_length=1)


class StockEntryResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    entry_number: str
    entry_type: str
    from_warehouse_id: Optional[uuid.UUID] = None
    to_warehouse_id: Optional[uuid.UUID] = None
    posting_date: date
    remarks: Optional[str] = None
    items: List[StockEntryItemResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Stock Balance & Valuation Report ---
class StockBalanceItem(BaseModel):
    product_id: uuid.UUID
    sku: str
    product_name: str
    warehouse_id: uuid.UUID
    warehouse_name: str
    current_quantity: Decimal
    valuation_rate: Decimal
    total_value: Decimal


# --- AI Low Stock & Stockout Alert ---
class LowStockAlertItem(BaseModel):
    product_id: uuid.UUID
    sku: str
    product_name: str
    current_stock: Decimal
    reorder_level: Decimal
    days_until_stockout: Optional[int] = None
    recommended_reorder_qty: Decimal
    urgency: str  # CRITICAL, WARNING, NORMAL
