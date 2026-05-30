from abc import ABC, abstractmethod
from app.schema import UserPersonalDetailCreate, UserPersonalDetailUpdate, UserPersonalDetailResponse

class IPersonalDetailsService(ABC):
    @abstractmethod
    async def create_personal_details(self, personal_details: UserPersonalDetailCreate, user_id: int) -> UserPersonalDetailResponse:
        pass

    @abstractmethod
    async def get_personal_details(self, user_id: int) -> UserPersonalDetailResponse | None:
        pass

    @abstractmethod
    async def update_personal_details(self, personal_details: UserPersonalDetailUpdate, user_id: int) -> UserPersonalDetailResponse:
        pass