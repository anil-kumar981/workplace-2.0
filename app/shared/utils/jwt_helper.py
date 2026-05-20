import jwt
from datetime import datetime, timedelta
from app.core import config
from app.shared.exceptions import AppException
from app.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

def _get_expires_delta() -> timedelta:
    """
    Parses the configured JWT expiration time.
    Supports hours ('h'), minutes ('m'), days ('d'), or raw seconds.
    """
    val = config.JWT_EXPIRES_IN
    if not val:
        return timedelta(hours=1)
    try:
        val = str(val).strip().lower()
        if val.endswith("h"):
            return timedelta(hours=int(val[:-1]))
        elif val.endswith("m"):
            return timedelta(minutes=int(val[:-1]))
        elif val.endswith("d"):
            return timedelta(days=int(val[:-1]))
        return timedelta(seconds=int(val))
    except Exception:
        return timedelta(hours=1)

def generate_jwt_token(user_id: int, email: str, expires_delta: timedelta = None) -> str:
    """
    Generates a secure JWT token for a given user.
    """
    if not expires_delta:
        expires_delta = _get_expires_delta()

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow()
    }

    try:
        token = jwt.encode(
            payload,
            config.JWT_SECRET_KEY,
            algorithm=config.JWT_ALGORITHM
        )
        return token
    except Exception as e:
        raise AppException(f"Failed to generate authentication token: {str(e)}", 500)

async def validate_jwt_token(token: str, db: AsyncSession) -> User:
    """
    Validates a JWT token, decodes it, and retrieves the corresponding User from the database.
    Raises an AppException (401 Unauthorized) if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise AppException("Authentication token has expired. Please log in again.", 401)
    except jwt.InvalidTokenError:
        raise AppException("Invalid authentication token. Please log in again.", 401)
    except Exception as e:
        raise AppException(f"Could not validate credentials: {str(e)}", 401)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AppException("Token is missing user identifier claim.", 401)

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise AppException("Invalid user identifier in token.", 401)

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise AppException("User account associated with this token was not found.", 401)

    if not user.is_active:
        raise AppException("This user account has been deactivated.", 401)

    return user
