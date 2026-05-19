from pydantic import Field, field_validator
from .user_base import UserBase

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validates password strength manually to support clean custom error messages
        and bypass Rust regex look-around limitations in Pydantic v2.
        """
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        
        special_characters = "@$!%*?&"
        if not any(c in special_characters for c in v):
            raise ValueError(f"Password must contain at least one special character from '{special_characters}'.")
            
        return v
