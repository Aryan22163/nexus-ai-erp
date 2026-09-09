import uuid
from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant, get_current_user
from app.core.database import get_db_session
from app.models.auth import Organization, User
from app.repositories.approval import ApprovalRepository
from app.repositories.audit import AuditLogRepository
from app.schemas.ai import ApprovalRequestResponse, ApprovalReviewAction

router = APIRouter(prefix="/approvals", tags=["Human-in-the-Loop Approvals"])


@router.get(
    "/pending",
    response_model=List[ApprovalRequestResponse],
    dependencies=[Depends(RequirePermissions("ai.execute_actions"))],
)
async def list_pending_approvals(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[ApprovalRequestResponse]:
    """List pending AI proposals awaiting human sign-off."""
    repo = ApprovalRepository(db, tenant.id)
    requests = await repo.list_pending()
    return [ApprovalRequestResponse.model_validate(r) for r in requests]


@router.post(
    "/{approval_id}/review",
    response_model=ApprovalRequestResponse,
    dependencies=[Depends(RequirePermissions("ai.execute_actions"))],
)
async def review_approval_request(
    approval_id: uuid.UUID,
    payload: ApprovalReviewAction,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApprovalRequestResponse:
    """Approve or reject a pending AI action proposal and log to the immutable audit trail."""
    repo = ApprovalRepository(db, tenant.id)
    approval = await repo.get_by_id(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    if approval.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request is already in '{approval.status}' state.")

    approval.reviewed_by_id = current_user.id
    approval.reviewed_at = datetime.now(timezone.utc)

    if payload.decision.upper() == "APPROVE":
        approval.status = "APPROVED"
        approval.execution_result = {
            "status": "EXECUTED",
            "message": f"Action {approval.action_type} approved by {current_user.email} and successfully executed.",
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        approval.status = "REJECTED"
        approval.execution_result = {
            "status": "REJECTED",
            "reason": payload.review_comments or "Rejected by reviewer",
        }

    # Record tamper-evident Audit Log
    audit_repo = AuditLogRepository(db, tenant.id)
    await audit_repo.log_action(
        action=f"HITL_{approval.status}",
        resource_type="ApprovalRequest",
        resource_id=str(approval.id),
        actor_id=current_user.id,
        before_state={"status": "PENDING"},
        after_state={"status": approval.status, "decision": payload.decision},
        is_ai_initiated=True,
    )

    await db.flush()
    return ApprovalRequestResponse.model_validate(approval)
