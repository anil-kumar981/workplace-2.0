from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.modules.users.router import router as user_router
from app.modules.auth.router import router as auth_router
from app.modules.users.personal_details.router import router as personal_details_router
from app.core import config
from app.middleware.exception_handler import register_exception_handlers
from app.middleware.logging_middleware import APILoggingMiddleware

# Instantiate global security scheme for Swagger UI "Authorize" button
security_scheme = HTTPBearer(auto_error=False)

# Instantiate modern, asynchronous FastAPI application context
app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    dependencies=[Depends(security_scheme)]
)

# Register request logging middleware
app.add_middleware(APILoggingMiddleware)

# Apply CORS (Cross-Origin Resource Sharing) middleware for smooth frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register centralized global exception handlers to capture system, client, and validation errors
register_exception_handlers(app)

# Mount modular routing layers under clean namespaces
app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(personal_details_router, prefix="/api")

@app.get("/", tags=["Health"])
async def root_health_check():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Enterprise Ledger & CRM Backend",
        "environment": config.ENV,
        "version": "1.0.0",
    }
