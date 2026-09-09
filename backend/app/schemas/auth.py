import uuid
from typing import List
from pydantic import BaseModel, EmailStr, Field
from app.schemas.organization import OrganizationResponse
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    """Company Admin onboarding: Registers both the Organization and its initial Root Administrator."""
    organization_name: str = Field(..., min_length=2, max_length=255, examples=["Nexus Retail Pvt Ltd"])
    currency: str = Field(default="INR", min_length=3, max_length=3, examples=["INR"])
    timezone: str = Field(default="Asia/Kolkata", examples=["Asia/Kolkata"])
    first_name: str = Field(..., min_length=1, max_length=100, examples=["Admin"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["User"])
    email: EmailStr = Field(..., examples=["admin@nexusretail.com"])
    password: str = Field(..., min_length=8, examples=["SuperSecurePass123!"])


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["admin@nexusretail.com"])
    password: str = Field(..., examples=["SuperSecurePass123!"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class CurrentUserContext(BaseModel):
    """Rich security context for currently authenticated session."""
    user: UserResponse
    organization: OrganizationResponse
    permissions: List[str]
