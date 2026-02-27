from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException


def _error_payload(code: str, message: str, detail: object | None = None) -> dict[str, object]:
    return {'error': {'code': code, 'message': message, 'detail': detail}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=_error_payload(exc.code, exc.message, exc.detail))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                'VALIDATION_ERROR',
                'Request body failed validation.',
                exc.errors(),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            payload = _error_payload('RESOURCE_NOT_FOUND', 'The requested resource was not found.', None)
        elif exc.status_code == 401:
            payload = _error_payload('UNAUTHORIZED', 'Authentication credentials were not provided or are invalid.', None)
        elif exc.status_code == 403:
            payload = _error_payload('FORBIDDEN', 'You do not have permission to perform this action.', None)
        else:
            payload = _error_payload('HTTP_ERROR', str(exc.detail), None)
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_error_payload('INTERNAL_SERVER_ERROR', 'An unexpected error occurred.', None),
        )