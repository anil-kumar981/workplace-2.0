from app.schema import UserResponse, UserCreate
from app.repos.user_repo import UserRepo
from app.shared.utils.security import hash_password
from app.shared.exceptions import AppException
from sqlalchemy.exc import IntegrityError
from .base_service import BaseService

class UserService(BaseService[UserRepo]):
    """
    UserService coordination layer.
    Manages transactional scope (commits/rollbacks) and coordinates business rules.
    """

    async def create_user_service(self, user: UserCreate) -> UserResponse:
        try:
            # 1. Hash the plain text password using the shared utility
            hashed_password = hash_password(user.password)
            
            # 2. Add user to the session via the repository
            new_user = await self.repo.create_user(user, hashed_password)
            
            # 3. Commit the transaction and refresh the entity state to populate ID/timestamps
            await self.repo.db.commit()
            await self.repo.db.refresh(new_user)
            
            # 4. Serialize to Pydantic Response
            return UserResponse.model_validate(new_user)
        except IntegrityError:
            await self.repo.db.rollback()
            raise AppException("An account with this email address already exists.", 400)
        except Exception as e:
            await self.repo.db.rollback()
            raise e

    async def get_all_users_service(self) -> list[UserResponse]:
        users = await self.repo.get_all_users()
        return [UserResponse.model_validate(u) for u in users]

    async def get_user_by_id_service(self, user_id: int) -> UserResponse | None:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

