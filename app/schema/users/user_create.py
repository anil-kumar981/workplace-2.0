from pydantic import Field
from .user_base import UserBase

class UserCreate(UserBase):
    hashed_password: str = Field(..., min_length=8, max_length=50, pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$")