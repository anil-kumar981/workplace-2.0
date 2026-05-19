import bcrypt
from app.core import config

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    Decodes the resulting bytes to a UTF-8 string for safe database storage.
    Uses the SALT_ROUNDS parameter configured in the central Config class.
    """
    # Generate bcrypt salt using configured rounds
    salt = bcrypt.gensalt(rounds=config.SALT_ROUNDS)
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored bcrypt hash string.
    Returns True if matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), 
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False
