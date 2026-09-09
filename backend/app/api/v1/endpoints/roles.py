from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.repositories.role import RoleRepository
from app.schemas.role import PermissionResponse, RoleResponse

router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[RoleResponse]:
    """List available system and custom roles within the active organization."""
    role_repo = RoleRepository(db, organization_id=tenant.id)
    roles = await role_repo.list_available_roles()
    return [RoleResponse.model_validate(r) for r in roles]


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[PermissionResponse]:
    """List all available granular system permissions."""
    role_repo = RoleRepository(db, organization_id=tenant.id)
    perms = await role_repo.list_permissions()
    return [PermissionResponse.model_validate(p) for p in perms]
