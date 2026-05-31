from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.shared.exceptions import AppException
from app.shared.api_response.api_response import ApiResponse
import traceback
import logging
import jwt
from app.core import config

# Setup logger for exceptions
logger = logging.getLogger("app.exceptions")
logger.setLevel(logging.ERROR)

def get_user_from_request(request: Request) -> str:
    """
    Helper to extract user identity (email or sub) safely from JWT or Query params
    without throwing exceptions or database queries.
    """
    user_identity = "Anonymous"
    
    # Try authorization header
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split()[1]
    
    # Try cookie fallback
    if not token:
        token = request.cookies.get(config.COOKIE_NAME)
        
    if token:
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM],
                options={"verify_signature": False} # Speed & safety in middleware
            )
            user_identity = payload.get("email") or payload.get("sub") or "Unknown User"
        except Exception:
            pass
            
    # Fallback to query parameters
    if user_identity == "Anonymous":
        email_param = request.query_params.get("email") or request.query_params.get("user_id")
        if email_param:
            user_identity = f"Param: {email_param}"
            
    return user_identity

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
        client_ip = request.client.host if request.client else "unknown"
        user = get_user_from_request(request)
        path = request.url.path
        
        err_msg = str(exc.orig) if exc.orig else str(exc)
        message = "A database integrity conflict occurred."

        # Parse common database unique constraints
        if "users_email_key" in err_msg or "uq_user" in err_msg:
            message = "An account with this email address already exists."
        elif "email" in err_msg:
            message = "This email address is already registered."
        elif "unique constraint" in err_msg.lower() or "duplicate key" in err_msg.lower():
            message = "This record already exists in the system."

        # Log detailed database error
        logger.error(
            f"[DATABASE INTEGRITY ERROR] {client_ip} | User: {user} | Path: {path} | Msg: {message} | Raw: {err_msg}"
        )

        return ApiResponse.fail(
            message=message,
            code=400
        )
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """
        Captures application level business validation exceptions (e.g. duplicate accounts).
        """
        client_ip = request.client.host if request.client else "unknown"
        user = get_user_from_request(request)
        path = request.url.path

        # Log custom application exceptions (like unauthorized or business logic fails)
        log_level = logging.WARNING if exc.code < 500 else logging.ERROR
        logger.log(
            log_level,
            f"[APPLICATION ERROR] {client_ip} | User: {user} | Path: {path} | Status Code: {exc.code} | Msg: {exc.message}"
        )

        return ApiResponse.fail(
            message=exc.message,
            code=exc.code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Captures automatic Pydantic model validation failures (e.g. invalid request format).
        """
        client_ip = request.client.host if request.client else "unknown"
        user = get_user_from_request(request)
        path = request.url.path

        # Log pydantic validation errors
        logger.warning(
            f"[VALIDATION FAILED] {client_ip} | User: {user} | Path: {path} | Errors: {exc.errors()}"
        )

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
        client_ip = request.client.host if request.client else "unknown"
        user = get_user_from_request(request)
        path = request.url.path

        # Log critical system failures with full traceback
        logger.critical(
            f"[CRITICAL SYSTEM FAILURE] {client_ip} | User: {user} | Path: {path} | Error: {str(exc)}"
        )
        traceback.print_exc() # Prints to server logs for developer debugging

        return ApiResponse.exception(
            exc,
            message="An unexpected system failure occurred while processing your request.",
            code=500
        )

