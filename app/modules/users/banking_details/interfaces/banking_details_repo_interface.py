from abc import ABC, abstractmethod

from app.models import BankingDetails
from app.schema import BankingDetailsCreate, BankingDetailsUpdate


class IBankingDetailsRepo(ABC):
    @abstractmethod
    async def create_banking_details(
        self, user_id: int, banking_details: BankingDetailsCreate
    ) -> BankingDetails:
        pass

    @abstractmethod
    async def update_banking_details(
        self, banking_details: BankingDetailsUpdate, user_id: int
    ) -> BankingDetails:
        pass

    @abstractmethod
    async def get_banking_details(self, user_id: int) -> BankingDetails:
        pass
