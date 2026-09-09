import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    actor_id: Optional[uuid.UUID]
    action: str
    resource_type: str
    resource_id: str
    before_state: Optional[dict[str, Any]] = None
    after_state: Optional[dict[str, Any]] = None
    is_ai_initiated: bool
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
