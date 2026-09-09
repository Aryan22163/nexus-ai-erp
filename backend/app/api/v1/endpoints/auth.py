from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_tenant, get_current_user
from app.core.database import get_db_session
from app.models.auth import Organization, User
from app.schemas.auth import (
    CurrentUserContext,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.organization import OrganizationResponse
from app.schemas.user import UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    """Register a new organization and root Company Admin account."""
    auth_service = AuthService(db)
    _, _, tokens = await auth_service.register_company(req)
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    """Authenticate with email and password, issuing access & refresh tokens."""
    auth_service = AuthService(db)
    _, tokens = await auth_service.authenticate(req)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    req: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    """Exchange a valid refresh token for a newly minted access token."""
    auth_service = AuthService(db)
    return await auth_service.refresh_access_token(req.refresh_token)


@router.get("/me", response_model=CurrentUserContext)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    tenant: Annotated[Organization, Depends(get_current_tenant)],
) -> CurrentUserContext:
    """Get the profile, organization info, and resolved permissions for the current user."""
    auth_service = AuthService(None)  # permissions extraction does not require db
    permissions = auth_service._extract_permissions(current_user)

    return CurrentUserContext(
        user=UserResponse.model_validate(current_user),
        organization=OrganizationResponse.model_validate(tenant),
        permissions=permissions,
    )
