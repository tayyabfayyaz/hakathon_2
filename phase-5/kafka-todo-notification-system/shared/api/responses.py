from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model for all API responses."""
    success: bool
    message: str
    timestamp: datetime = None

    def __init__(self, **data):
        super().__init__(timestamp=datetime.utcnow(), **data)


class TodoResponse(BaseResponse):
    """Response model for todo operations."""
    data: Optional[Dict[str, Any]] = None


class TodoListResponse(BaseResponse):
    """Response model for todo list operations."""
    data: List[Dict[str, Any]] = []
    total_count: int = 0


class UserPreferencesResponse(BaseResponse):
    """Response model for user preferences operations."""
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseResponse):
    """Response model for error scenarios."""
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    @classmethod
    def create_error(cls, message: str, error_code: str = None, details: Dict[str, Any] = None):
        return cls(success=False, message=message, error_code=error_code, details=details)


class HealthCheckResponse(BaseResponse):
    """Response model for health check endpoints."""
    service: str
    version: str
    uptime: Optional[str] = None
    status_details: Optional[Dict[str, Any]] = None