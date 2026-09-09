import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Branch Schemas ---
class BranchBase(BaseModel):
    name: str = Field(..., examples=["Bangalore Flagship Branch"])
    code: str = Field(..., examples=["BLR-01"])
    address: Optional[str] = Field(None, examples=["12th Main, Indiranagar"])
    city: Optional[str] = Field(None, examples=["Bangalore"])
    country: str = Field(default="India")
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchResponse(BranchBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Department Schemas ---
class DepartmentBase(BaseModel):
    name: str = Field(..., examples=["Supply Chain Operations"])
    code: str = Field(..., examples=["OPS-SC"])
    parent_id: Optional[uuid.UUID] = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Warehouse Schemas ---
class WarehouseBase(BaseModel):
    name: str = Field(..., examples=["Central Distribution Center"])
    code: str = Field(..., examples=["WH-MAIN"])
    branch_id: Optional[uuid.UUID] = None
    address: Optional[str] = Field(None, examples=["Plot 44, Electronic City Phase 1"])
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseResponse(WarehouseBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Fiscal Year Schemas ---
class FiscalYearBase(BaseModel):
    name: str = Field(..., examples=["FY 2026-2027"])
    start_date: date = Field(..., examples=["2026-04-01"])
    end_date: date = Field(..., examples=["2027-03-31"])
    is_closed: bool = False


class FiscalYearCreate(FiscalYearBase):
    pass


class FiscalYearResponse(FiscalYearBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Tax Configuration Schemas ---
class TaxConfigurationBase(BaseModel):
    name: str = Field(..., examples=["Standard GST 18%"])
    code: str = Field(..., examples=["GST-18"])
    rate: Decimal = Field(..., examples=[Decimal("18.00")])
    tax_type: str = Field(default="GST", examples=["GST"])
    is_active: bool = True


class TaxConfigurationCreate(TaxConfigurationBase):
    pass


class TaxConfigurationResponse(TaxConfigurationBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
