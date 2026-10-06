from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.ai_recommender import ai_recommender_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def check_health():
    """
    Standard liveness probe for the backend API.
    """
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/ready", response_model=ReadinessResponse)
async def check_readiness():
    """
    Readiness probe indicating if Supabase, database, and Gemini are configured.
    """
    db_configured = bool(settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL)
    supabase_configured = bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)
    gemini_configured = ai_recommender_service.is_configured()

    return ReadinessResponse(
        status="ready" if (supabase_configured or settings.ENVIRONMENT == "development") else "unconfigured",
        database_configured=db_configured,
        supabase_configured=supabase_configured,
        gemini_configured=gemini_configured,
        details={
            "environment": settings.ENVIRONMENT,
            "project_name": settings.PROJECT_NAME,
            "gemini_model": settings.GEMINI_MODEL,
        },
    )
