from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.shared.exceptions import AppException
from app.shared.api_response.api_response import ApiResponse
import traceback

def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers all global exception handlers to clean up and simplify app/__init__.py
    """

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """
        Captures database integrity constraint violations globally (e.g. unique constraint failures).
        Translates raw database error messages into clean, user-friendly responses.
        """
        err_msg = str(exc.orig) if exc.orig else str(exc)
        message = "A database integrity conflict occurred."

        # Parse common database unique constraints
        if "users_email_key" in err_msg or "uq_user" in err_msg:
            message = "An account with this email address already exists."
        elif "email" in err_msg:
            message = "This email address is already registered."
        elif "unique constraint" in err_msg.lower() or "duplicate key" in err_msg.lower():
            message = "This record already exists in the system."

        return ApiResponse.fail(
            message=message,
            code=400
        )
    
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
