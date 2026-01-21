"""Error response schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str = Field(
        description="Error code identifier",
        examples=["VALIDATION_ERROR", "UNAUTHORIZED", "NOT_FOUND"]
    )
    message: str = Field(
        description="Human-readable error message"
    )
    details: Optional[list[str]] = Field(
        default=None,
        description="Additional error details"
    )


class ValidationErrorDetail(BaseModel):
    """Validation error detail for 422 responses."""

    loc: list[str]
    msg: str
    type: str
