from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Liveness and health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
    )


@router.get("/health/ready", response_model=HealthResponse, tags=["Health"])
async def readiness_check() -> HealthResponse:
    """Readiness probe endpoint for Kubernetes / Cloud orchestrators."""
    return HealthResponse(
        status="ready",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
    )
