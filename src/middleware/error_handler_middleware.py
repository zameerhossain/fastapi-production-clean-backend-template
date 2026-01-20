import traceback

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.exceptions.exceptions import BusinessException
from src.logger.logger import logger


async def error_handler_middleware(request: Request, exc: Exception) -> JSONResponse:
    # Business/domain exceptions
    if isinstance(exc, BusinessException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.message},
        )

    # DB unique constraint, FK violation, etc
    if isinstance(exc, IntegrityError):
        logger.warning(f"IntegrityError: {exc}")
        return JSONResponse(
            status_code=409,
            content={"success": False, "error": "Resource already exists"},
        )

    # Other SQLAlchemy errors
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"SQLAlchemyError: {exc}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Database error"},
        )

    # Validation errors
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"success": False, "error": exc.errors()},
        )

    # Fallback
    logger.error(f"Unhandled Exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )
