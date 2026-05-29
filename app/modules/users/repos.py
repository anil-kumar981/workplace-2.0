from sqlalchemy import select
from app.models.users import User
from app.schema import UserCreate
from app.shared.base_repo import BaseRepo
from .interfaces.user_repo_interface import IUserRepo


class UserRepo(BaseRepo, IUserRepo):
    async def create_user(self, user_create: UserCreate, hashed_password: str) -> User:
        new_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            role_id=user_create.role_id,
        )
        self.db.add(new_user)
        return new_user

    async def get_all_users(self) -> list[User]:
        stmt = select(User)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_by_id(self, id: int) -> User | None:
        stmt = select(User).where(User.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_user_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        self.db.add(user)
        return user
