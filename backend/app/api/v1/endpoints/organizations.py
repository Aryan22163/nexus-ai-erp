from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant, get_current_user
from app.core.database import get_db_session
from app.models.auth import Organization, User
from app.schemas.organization import OrganizationResponse, OrganizationUpdate

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/current", response_model=OrganizationResponse)
async def get_current_organization(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
) -> OrganizationResponse:
    """Retrieve details of the active organization."""
    return OrganizationResponse.model_validate(tenant)


@router.patch(
    "/current",
    response_model=OrganizationResponse,
    dependencies=[Depends(RequirePermissions("organization.update"))],
)
async def update_current_organization(
    payload: OrganizationUpdate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> OrganizationResponse:
    """Update settings of the active organization (requires organization.update)."""
    if payload.name is not None:
        tenant.name = payload.name
    if payload.currency is not None:
        tenant.currency = payload.currency
    if payload.timezone is not None:
        tenant.timezone = payload.timezone

    await db.flush()
    await db.refresh(tenant)
    return OrganizationResponse.model_validate(tenant)
