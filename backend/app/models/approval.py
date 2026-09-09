import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.auth import User
from app.models.base import TenantBaseModel


class ApprovalRequest(TenantBaseModel):
    """
    Human-in-the-Loop (HITL) Action Proposal.
    Whenever AI proposes a mutating business action (e.g. issuing PO, creating Sales Order, modifying financial entries),
    an ApprovalRequest is persisted requiring explicit human review before execution.
    """
    __tablename__ = "approval_requests"

    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # CREATE_PURCHASE_ORDER, CREATE_SALES_ORDER, POST_JOURNAL_ENTRY
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True,
    )  # PENDING, APPROVED, REJECTED, EXECUTED
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    requester_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_result: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )

    requester: Mapped[Optional["User"]] = relationship("User", foreign_keys=[requester_id])
    reviewed_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by_id])
