"""Consistent API exception response models and handlers."""

import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def install_exception_handlers(app: FastAPI) -> None:
    """Install non-leaking validation and unexpected-error handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": error.errors()})

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
        error_id = str(uuid4())
        logger.exception(
            "Unhandled API exception", extra={"request_id": request.headers.get("X-Request-ID")}
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected server error occurred.", "error_id": error_id},
        )
