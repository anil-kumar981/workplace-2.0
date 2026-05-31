from sqlalchemy import select

from app.models import BankingDetails
from app.schema import BankingDetailsCreate, BankingDetailsUpdate
from app.shared.base_repo import BaseRepo

from .interfaces.banking_details_repo_interface import IBankingDetailsRepo


class BankingDetailsRepo(BaseRepo, IBankingDetailsRepo):
    async def create_banking_details(
        self, user_id: int, banking_details: BankingDetailsCreate
    ) -> BankingDetails:

        banking_details = BankingDetails(**banking_details.dict(), user_id=user_id)
        self.db.add(banking_details)
        await self.db.commit()
        await self.db.refresh(banking_details)
        return banking_details

    async def get_banking_details(self, user_id: int) -> BankingDetails:
        stmt = select(BankingDetails).where(BankingDetails.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_banking_details(
        self, banking_details: BankingDetailsUpdate, user_id: int
    ) -> BankingDetails:
        banking_detail = await self.get_banking_details(user_id)
        if not banking_detail:
            from app.shared.exceptions import AppException

            raise AppException("Banking details not found for the specified user.", 404)

        update_data = banking_details.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(banking_detail, key, value)
        self.db.add(banking_detail)
        await self.db.commit()
        await self.db.refresh(banking_detail)
        return banking_detail

