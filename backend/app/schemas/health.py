from datetime import datetime, timezone
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    app_name: str = Field(..., examples=["NEXUS AI"])
    environment: str = Field(..., examples=["development"])
    version: str = Field(..., examples=["0.1.0"])
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
