from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from app.shared.exceptions import AppException
from app.shared.api_response.api_response import ApiResponse
import traceback

def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers all global exception handlers to clean up and simplify app/__init__.py
    """
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """
        Captures application level business validation exceptions (e.g. duplicate accounts).
        """
        return ApiResponse.fail(
            message=exc.message,
            code=exc.code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Captures automatic Pydantic model validation failures (e.g. invalid request format).
        """
        return ApiResponse.fail(
            data=exc.errors(),
            message="Request validation failed. Please check your inputs.",
            code=422
        )

    @app.exception_handler(Exception)
    async def global_unexpected_exception_handler(request: Request, exc: Exception):
        """
        Catch-all safety net to protect against unhandled system exceptions (e.g. database down).
        """
        traceback.print_exc() # Prints to server logs for developer debugging
        return ApiResponse.exception(
            exc,
            message="An unexpected system failure occurred while processing your request.",
            code=500
        )
