from app.schema import UserResponse, UserCreate
from app.repos.user_repo import UserRepo
from app.shared.utils.security import hash_password
from .base_service import BaseService

class UserService(BaseService[UserRepo]):
    """
    UserService inherits from BaseService[UserRepo].
    Coordinates high-level business rules for Users.
    """

    async def create_user_service(self, user: UserCreate) -> UserResponse:
        try:
            # 1. Hash the plain text password using the shared utility (which uses central SALT_ROUNDS)
            hashed_password = hash_password(user.password)
            
            # 2. Save the user to the database using the asynchronous repository
            new_user = await self.repo.create_user(user, hashed_password)
            
            # 3. Validate and serialize the SQLAlchemy model to a Pydantic response schema
            return UserResponse.model_validate(new_user)
        except Exception as e:
            raise e

    async def get_all_users_service(self) -> list[UserResponse]:
        try:
            users = await self.repo.get_all_users()
            return [UserResponse.model_validate(u) for u in users]
        except Exception as e:
            raise e

    async def get_user_by_id_service(self, user_id: int) -> UserResponse | None:
        try:
            user = await self.repo.get_user_by_id(user_id)
            if not user:
                return None
            return UserResponse.model_validate(user)
        except Exception as e:
            raise e

