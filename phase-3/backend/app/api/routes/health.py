"""Health check endpoint."""

from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database import get_session
from app.schemas.health import HealthResponse

settings = get_settings()
router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check API health status.

    Returns the health status of the API including:
    - Overall status (healthy/unhealthy)
    - Database connection status
    - API version
    """
    # Check database connectivity
    database_status = "connected"
    try:
        async for session in get_session():
            await session.execute(text("SELECT 1"))
            break
    except Exception:
        database_status = "disconnected"

    overall_status = "healthy" if database_status == "connected" else "unhealthy"

    return HealthResponse(
        status=overall_status,
        database=database_status,
        version=settings.api_version,
    )
