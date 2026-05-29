from abc import ABC, abstractmethod
from app.models.users import User
from app.schema import UserCreate

class IUserRepo(ABC):
    @abstractmethod
    async def create_user(self, user_create: UserCreate, hashed_password: str) -> User:
        """
        Adds a new User entity to the current database session state.
        Transaction commit is handled at the Service layer.
        """
        pass

    @abstractmethod
    async def get_all_users(self) -> list[User]:
        """
        Retrieves all user records from the database.
        """
        pass

    @abstractmethod
    async def get_user_by_id(self, id: int) -> User | None:
        """
        Finds a user record by its primary key identifier.
        """
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """
        Finds a user record by its email address.
        """
        pass

    @abstractmethod
    async def update_user_password(self, user: User, hashed_password: str) -> User:
        """
        Updates the user's password hash.
        """
        pass
