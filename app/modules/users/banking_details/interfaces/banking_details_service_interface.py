from abc import ABC, abstractmethod

from app.schema import (
    BankingDetailsCreate,
    BankingDetailsResponse,
    BankingDetailsUpdate,
)


class IBankingDetailsService(ABC):
    @abstractmethod
    async def create_banking_details(
        self, user_id: int, banking_details: BankingDetailsCreate
    ) -> BankingDetailsResponse:
        pass

    @abstractmethod
    async def update_banking_details(
        self, user_id: int, banking_details: BankingDetailsUpdate
    ) -> BankingDetailsResponse:
        pass

    @abstractmethod
    async def get_banking_details(self, user_id: int) -> BankingDetailsResponse:
        pass

