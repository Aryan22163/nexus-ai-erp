from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.schemas.dashboard import ExecutiveDashboardSummary
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard & Analytics"])


@router.get(
    "/executive-summary",
    response_model=ExecutiveDashboardSummary,
    dependencies=[Depends(RequirePermissions("organization.read"))],
)
async def get_executive_summary(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExecutiveDashboardSummary:
    """Consolidated executive dashboard summary aggregating financial, sales, inventory, and AI insights."""
    service = DashboardService(db, tenant.id)
    return await service.get_executive_summary()
