from abc import ABC, abstractmethod
from app.models import UserPersonalDetails, User
from app.schema import UserPersonalDetailCreate, UserPersonalDetailUpdate

class IPersonalDetailsRepo(ABC):
    @abstractmethod
    async def create_personal_details(self, personal_details: UserPersonalDetailCreate, user_id: int) -> UserPersonalDetails:
        pass

    @abstractmethod
    async def get_personal_details(self, user_id: int) -> UserPersonalDetails | None:
        pass

    @abstractmethod
    async def update_personal_details(self, personal_details: UserPersonalDetailUpdate, user_id: int) -> UserPersonalDetails:
        pass
