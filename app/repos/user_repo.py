from sqlalchemy import select
from app.models.users import User
from .base_repo import BaseRepo
from app.schema import UserCreate


class UserRepo(BaseRepo):
    async def create_user(self, user_create: UserCreate, hashed_password: str) -> User:
        """
        Adds a new User entity to the current database session state.
        Transaction commit is handled at the Service layer.
        """
        new_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            role_id=user_create.role_id,
        )
        self.db.add(new_user)
        return new_user

    async def get_all_users(self) -> list[User]:
        """
        Retrieves all user records from the database.
        """
        stmt = select(User)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_by_id(self, id: int) -> User | None:
        """
        Finds a user record by its primary key identifier.
        """
        stmt = select(User).where(User.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
