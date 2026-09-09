import uuid
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Chat & Copilot Messages ---
class AIChatMessage(BaseModel):
    role: str = Field(..., examples=["user"])  # user, assistant, system, tool
    content: str = Field(..., examples=["Why did revenue decline this month?"])


class AICopilotRequest(BaseModel):
    prompt: str = Field(..., min_length=2, examples=["Show our top 5 customers and their revenue."])
    conversation_history: List[AIChatMessage] = Field(default_factory=list)


class ActionProposalCard(BaseModel):
    approval_request_id: uuid.UUID
    action_type: str
    summary: str
    explanation: str
    proposed_payload: dict[str, Any]
    status: str = "PENDING"


class AICopilotResponse(BaseModel):
    reply: str
    intent: str
    executed_tools: List[str] = Field(default_factory=list)
    action_proposal: Optional[ActionProposalCard] = None
    citations: List[str] = Field(default_factory=list)


# --- Approval Review Schemas ---
class ApprovalReviewAction(BaseModel):
    decision: str = Field(..., examples=["APPROVE"])  # APPROVE, REJECT
    review_comments: Optional[str] = None


class ApprovalRequestResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    action_type: str
    status: str
    explanation: str
    payload: dict[str, Any]
    execution_result: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
