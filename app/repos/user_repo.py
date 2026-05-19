from sqlalchemy import select
from app.models.users import User
from .base_repo import BaseRepo
from app.schema import UserCreate


class UserRepo(BaseRepo):
    async def create_user(self, user_create: UserCreate, hashed_password: str) -> User:
        try:
            new_user = User(
                email=user_create.email,
                username=user_create.username,
                hashed_password=hashed_password,
                role_id=user_create.role_id,
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_all_users(self) -> list[User]:
        try:
            stmt = select(User)
            result = await self.db.execute(stmt)
            users = result.scalars().all()
            return list(users)
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_user_by_id(self, id: int) -> User | None:
        try:
            stmt = select(User).where(User.id == id)
            result = await self.db.execute(stmt)
            user = result.scalars().first()
            return user
        except Exception as e:
            await self.db.rollback()
            raise e
