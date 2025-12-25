from typing import Optional, List
from pydantic import BaseModel


class ValidationErrorDetail(BaseModel):
    field: str
    error: str


class ErrorDetails(BaseModel):
    fields: Optional[List[ValidationErrorDetail]] = None


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[ErrorDetails] = None
