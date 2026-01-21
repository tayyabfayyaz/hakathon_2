"""Health check response schema."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "unhealthy"]
    database: Literal["connected", "disconnected"]
    version: str
