import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    email: EmailStr = Field(..., examples=["admin@nexusretail.com"])
    first_name: str = Field(..., min_length=1, max_length=100, examples=["Aryan"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Sharma"])


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, examples=["SuperSecurePass123!"])
    role_ids: List[uuid.UUID] = Field(default_factory=list)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[uuid.UUID]] = None


class UserResponse(UserBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    is_active: bool
    is_superuser: bool
    roles: List[RoleResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
