import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import NexusException
from app.core.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for startup and shutdown procedures."""
    setup_logging()
    logger.info(
        "nexus_startup",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        debug=settings.DEBUG,
    )
    yield
    logger.info("nexus_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Native Business Operating System combining ERP, CRM, Finance, Inventory, HR, and Autonomous Agents.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_and_timing_middleware(request: Request, call_next):
    """Assigns unique correlation ID and logs execution duration for observability."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(process_time, 2),
        correlation_id=correlation_id,
    )
    return response


@app.exception_handler(NexusException)
async def nexus_exception_handler(request: Request, exc: NexusException):
    """Unified handler for domain-level Nexus exceptions."""
    logger.warning(
        "domain_exception",
        error=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.message, "details": exc.details},
    )


# Include API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "tagline": "AI-Native Business Operating System",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "web_app": "/app",
    }


# Mount deployable light-theme static frontend
_web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web")
if not os.path.exists(_web_dir):
    _web_dir = os.path.join(os.getcwd(), "web")

if os.path.exists(_web_dir):
    app.mount("/app", StaticFiles(directory=_web_dir, html=True), name="web_app")
