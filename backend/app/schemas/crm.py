import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Contact Schemas ---
class ContactBase(BaseModel):
    first_name: str = Field(..., examples=["Rajesh"])
    last_name: str = Field(..., examples=["Kumar"])
    email: Optional[EmailStr] = Field(None, examples=["rajesh@acmecorp.com"])
    phone: Optional[str] = Field(None, examples=["+91 98765 43210"])
    designation: Optional[str] = Field(None, examples=["Procurement VP"])
    is_primary: bool = False


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Customer Schemas ---
class CustomerBase(BaseModel):
    name: str = Field(..., examples=["Acme Retail Enterprise"])
    email: Optional[EmailStr] = Field(None, examples=["procurement@acmeretail.com"])
    phone: Optional[str] = Field(None, examples=["+91 80 4433 2211"])
    tax_identifier: Optional[str] = Field(None, examples=["29ABCDE1234F1Z5"])
    billing_address: Optional[dict[str, Any]] = None
    shipping_address: Optional[dict[str, Any]] = None
    credit_limit: Decimal = Field(default=Decimal("100000.00"), examples=[Decimal("500000.00")])
    customer_segment: str = Field(default="SMB", examples=["ENTERPRISE"])
    churn_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    is_active: bool = True


class CustomerCreate(CustomerBase):
    contacts: List[ContactCreate] = Field(default_factory=list)


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tax_identifier: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    customer_segment: Optional[str] = None
    churn_risk_score: Optional[float] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    contacts: List[ContactResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Lead Schemas ---
class LeadBase(BaseModel):
    first_name: str = Field(..., examples=["Vikram"])
    last_name: str = Field(..., examples=["Patel"])
    company_name: Optional[str] = Field(None, examples=["Patel Logistics"])
    email: Optional[EmailStr] = Field(None, examples=["vikram@patellogistics.com"])
    phone: Optional[str] = Field(None, examples=["+91 91234 56789"])
    source: str = Field(default="WEBSITE", examples=["WEBSITE"])
    status: str = Field(default="NEW", examples=["NEW"])
    score: float = Field(default=50.0, ge=0.0, le=100.0)
    assigned_to_id: Optional[uuid.UUID] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    score: Optional[float] = None
    assigned_to_id: Optional[uuid.UUID] = None


class LeadResponse(LeadBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    converted_customer_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Opportunity Schemas ---
class OpportunityBase(BaseModel):
    customer_id: uuid.UUID
    title: str = Field(..., examples=["Annual Logistics Software Contract"])
    stage: str = Field(default="PROSPECTING", examples=["PROPOSAL"])
    amount: Decimal = Field(..., examples=[Decimal("2500000.00")])
    probability: float = Field(default=20.0, ge=0.0, le=100.0)
    expected_close_date: Optional[date] = Field(None, examples=["2026-11-30"])
    assigned_to_id: Optional[uuid.UUID] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityResponse(OpportunityBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Activity Schemas ---
class ActivityBase(BaseModel):
    entity_type: str = Field(..., examples=["CUSTOMER"])
    entity_id: uuid.UUID
    activity_type: str = Field(..., examples=["MEETING"])
    title: str = Field(..., examples=["Quarterly Pricing Review"])
    details: Optional[str] = Field(None, examples=["Client requested 5% bulk rebate for Q4"])
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- AI Summary Schema ---
class CustomerAISummaryResponse(BaseModel):
    customer_id: uuid.UUID
    customer_name: str
    segment: str
    churn_risk: float
    total_opportunities: int
    open_pipeline_value: Decimal
    recent_activities_count: int
    ai_summary: str
    recommended_actions: List[str]
