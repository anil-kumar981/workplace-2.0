import time
import logging
import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core import config

# Setup standard logger
logger = logging.getLogger("app.api")
logger.setLevel(logging.INFO)

# Ensure handler exists
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class APILoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log every incoming API request and outgoing response,
    including execution time, status code, and user identity.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query = f"?{request.url.query}" if request.url.query else ""
        
        # Extract user identity safely from JWT or Query params
        user_identity = "Anonymous"
        
        # 1. Try to extract from Authorization Bearer header
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split()[1]
        
        # 2. Try to extract from secure cookie
        if not token:
            token = request.cookies.get(config.COOKIE_NAME)
            
        if token:
            try:
                # Decode payload without signature verification for speed in middleware
                payload = jwt.decode(
                    token,
                    config.JWT_SECRET_KEY,
                    algorithms=[config.JWT_ALGORITHM],
                    options={"verify_signature": False}
                )
                user_identity = payload.get("email") or payload.get("sub") or "Unknown User"
            except Exception:
                pass
                
        # 3. Fallback to query params if anonymous (useful for register/login/otp flows)
        if user_identity == "Anonymous":
            email_param = request.query_params.get("email") or request.query_params.get("user_id")
            if email_param:
                user_identity = f"Param: {email_param}"

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Formulate status message
            status_code = response.status_code
            
            # Log success/failure cleanly
            if status_code >= 400:
                logger.warning(
                    f'{client_ip} - "{method} {path}{query}" {status_code} FAILURE | User: {user_identity} | Duration: {process_time:.3f}s'
                )
            else:
                logger.info(
                    f'{client_ip} - "{method} {path}{query}" {status_code} SUCCESS | User: {user_identity} | Duration: {process_time:.3f}s'
                )
                
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f'{client_ip} - "{method} {path}{query}" 500 CRITICAL ERROR | User: {user_identity} | Error: {str(exc)} | Duration: {process_time:.3f}s'
            )
            raise exc
