import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PermissionResponse(BaseModel):
    id: uuid.UUID
    code: str = Field(..., examples=["sales.read"])
    module: str = Field(..., examples=["sales"])
    description: str

    model_config = ConfigDict(from_attributes=True)


class RoleBase(BaseModel):
    name: str = Field(..., examples=["Sales Manager"])
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_codes: List[str] = Field(default_factory=list)


class RoleResponse(RoleBase):
    id: uuid.UUID
    is_system: bool
    permissions: List[PermissionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
