from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import OneShotAPIError
from .logging import log_error
from .responses import create_error_response


async def one_shot_api_error_handler(
    request: Request, exc: OneShotAPIError
) -> JSONResponse:
    """Global error handler for OneShotAPIError exceptions.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse: Error response
    """
    # Log the error with request context
    log_error(
        request.app.logger,
        exc,
        {
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else None,
        },
    )

    # Create standardized error response
    error_response = create_error_response(
        error=exc.__class__.__name__, message=str(exc), status_code=exc.status_code
    )

    return JSONResponse(status_code=exc.status_code, content=error_response.dict())


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global error handler for unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse: Error response
    """
    # Log the error with request context
    log_error(
        request.app.logger,
        exc,
        {
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else None,
        },
    )

    # Create standardized error response
    error_response = create_error_response(
        error="InternalServerError",
        message="An unexpected error occurred",
        status_code=500,
    )

    return JSONResponse(status_code=500, content=error_response.dict())
