"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from respira_ally.core.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="RespiraAlly V2.0 - COPD Patient Healthcare Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - Health check."""
    return {
        "status": "healthy",
        "service": "RespiraAlly Backend API",
        "version": settings.PROJECT_VERSION,
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    """Application startup event handler."""
    logger.info("application_startup", version=settings.PROJECT_VERSION)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Application shutdown event handler."""
    logger.info("application_shutdown")


# Import and include API routers (will be uncommented as they are implemented)
# from respira_ally.api.v1 import auth, patients, daily_logs
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
# app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
# app.include_router(daily_logs.router, prefix="/api/v1/daily-logs", tags=["daily-logs"])
