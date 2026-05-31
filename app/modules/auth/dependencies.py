from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import config
from app.database.sessions import get_db
from app.models.users import User
from app.modules.users.dependencies import get_user_repo
from app.modules.users.interfaces.user_repo_interface import IUserRepo
from app.shared.exceptions import AppException
from app.shared.utils.jwt_helper import validate_jwt_token

from .repos import OtpRepo
from .services import AuthService


def get_otp_repo(db: AsyncSession = Depends(get_db)) -> OtpRepo:
    """
    Dependency provider to instantiate OtpRepo with an active DB session.
    """
    return OtpRepo(db)


def get_auth_service(
    user_repo: IUserRepo = Depends(get_user_repo),
    otp_repo: OtpRepo = Depends(get_otp_repo),
) -> AuthService:
    """
    Dependency provider to instantiate AuthService with both UserRepo and OtpRepo.
    """
    return AuthService(user_repo, otp_repo)


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency that extracts the JWT token from either:
    1. The Authorization header (Bearer token)
    2. The configured secure HttpOnly cookie
    Then validates the token and returns the corresponding User model.
    """
    token = None

    # 1. Try to extract from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    # 2. If not found in header, try the secure cookie
    if not token:
        token = request.cookies.get(config.COOKIE_NAME)

    if not token:
        raise AppException(
            "Authentication credentials were not provided. Please log in.", 401
        )

    return await validate_jwt_token(token, db)
