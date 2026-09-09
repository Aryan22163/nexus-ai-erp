import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, examples=["Nexus Retail Pvt Ltd"])
    currency: str = Field(default="INR", min_length=3, max_length=3, examples=["INR"])
    timezone: str = Field(default="Asia/Kolkata", examples=["Asia/Kolkata"])


class OrganizationCreate(OrganizationBase):
    slug: Optional[str] = Field(None, min_length=2, max_length=100, examples=["nexus-retail"])


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
