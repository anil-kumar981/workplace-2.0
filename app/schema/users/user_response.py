from datetime import datetime
from .user_base import UserBase


class UserResponse(UserBase):
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime