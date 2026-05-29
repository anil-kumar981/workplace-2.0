from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.users.router import router as user_router
from app.modules.auth.router import router as auth_router
from app.core import config
from app.middleware.exception_handler import register_exception_handlers

# Instantiate modern, asynchronous FastAPI application context
app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
)

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
