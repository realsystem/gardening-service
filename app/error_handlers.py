"""Custom error handlers for consistent API error responses"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError


def map_status_to_code(status_code: int) -> str:
    """Map HTTP status codes to error codes"""
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
    }
    return code_map.get(status_code, "UNKNOWN_ERROR")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with consistent error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": map_status_to_code(exc.status_code),
                "message": exc.detail
            }
        },
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with consistent error format"""
    # Extract validation error details
    errors = exc.errors()
    if errors:
        # Build a user-friendly message from validation errors
        messages = []
        for error in errors:
            field = " -> ".join(str(x) for x in error["loc"])
            msg = error["msg"]
            messages.append(f"{field}: {msg}")
        message = "; ".join(messages)
    else:
        message = "Validation error"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with consistent error format"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
