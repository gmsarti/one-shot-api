from typing import Any, Dict, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None


def create_error_response(
    error: str, message: str, status_code: int, details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create a standardized error response.

    Args:
        error: The error type/name
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details

    Returns:
        ErrorResponse: Standardized error response
    """
    return ErrorResponse(
        error=error, message=message, status_code=status_code, details=details
    )
