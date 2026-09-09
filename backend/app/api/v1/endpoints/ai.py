from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.agents.orchestrator import AICopilotOrchestrator
from app.api.deps import RequirePermissions, get_current_tenant, get_current_user
from app.core.database import get_db_session
from app.models.auth import Organization, User
from app.schemas.ai import AICopilotRequest, AICopilotResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/ai", tags=["AI Copilot & Agents"])


@router.post(
    "/copilot",
    response_model=AICopilotResponse,
    dependencies=[Depends(RequirePermissions("ai.copilot"))],
)
async def chat_with_copilot(
    req: AICopilotRequest,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AICopilotResponse:
    """
    Interact with NEXUS AI Enterprise Copilot.
    Executes domain queries and formulates safe action proposals with human-in-the-loop approvals.
    """
    auth_service = AuthService(None)
    permissions = auth_service._extract_permissions(current_user)

    orchestrator = AICopilotOrchestrator(
        session=db,
        organization_id=tenant.id,
        user_id=current_user.id,
        user_permissions=permissions,
    )
    return await orchestrator.process_prompt(req)
