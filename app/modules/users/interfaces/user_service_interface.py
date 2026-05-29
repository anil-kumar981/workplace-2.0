from abc import ABC, abstractmethod
from app.schema import UserCreate, UserResponse

class IUserService(ABC):
    @abstractmethod
    async def create_user_service(self, user: UserCreate) -> UserResponse:
        """
        Creates a new user service entry and coordinates transactions/business rules.
        """
        pass

    @abstractmethod
    async def get_all_users_service(self) -> list[UserResponse]:
        """
        Retrieves all users formatted as UserResponse.
        """
        pass

    @abstractmethod
    async def get_user_by_id_service(self, user_id: int) -> UserResponse | None:
        """
        Finds a user by ID and formats it as UserResponse or None.
        """
        pass
