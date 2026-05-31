from app.modules.users.interfaces.user_service_interface import IUserService
from app.schema import (
    BankingDetailsCreate,
    BankingDetailsResponse,
    BankingDetailsUpdate,
)
from app.shared.exceptions import AppException

from .interfaces.banking_details_repo_interface import IBankingDetailsRepo
from .interfaces.banking_details_service_interface import IBankingDetailsService


class BankingDetailsService(IBankingDetailsService):
    def __init__(self, repo: IBankingDetailsRepo, user_service: IUserService):
        self.repo = repo
        self.user_service = user_service

    async def create_banking_details(
        self, user_id: int, banking_details: BankingDetailsCreate
    ) -> BankingDetailsResponse:
        try:
            user = await self.user_service.get_user_by_id_service(user_id)
            if not user:
                raise AppException("User not found", 404)
            
            # Check if banking details already exist
            existing = await self.repo.get_banking_details(user_id)
            if existing:
                raise AppException("Banking details already exist for this user. Use update instead.", 400)

            db_banking_details = await self.repo.create_banking_details(
                user_id, banking_details
            )
            return BankingDetailsResponse.model_validate(db_banking_details)
        except Exception as e:
            raise e

    async def get_banking_details(self, user_id: int) -> BankingDetailsResponse:
        try:
            user = await self.user_service.get_user_by_id_service(user_id)
            if not user:
                raise AppException("User not found", 404)
                
            banking_detail = await self.repo.get_banking_details(user_id)
            if not banking_detail:
                raise AppException("Banking details not found for the specified user.", 404)
                
            return BankingDetailsResponse.model_validate(banking_detail)
        except Exception as e:
            raise e

    async def update_banking_details(
        self, user_id: int, banking_details: BankingDetailsUpdate
    ) -> BankingDetailsResponse:
        try:
            user = await self.user_service.get_user_by_id_service(user_id)
            if not user:
                raise AppException("User not found", 404)

            check_existing = await self.repo.get_banking_details(user_id)
            if not check_existing:
                raise AppException("Banking details not found for the provided user.", 404)

            banking_detail = await self.repo.update_banking_details(
                banking_details, user_id
            )
            return BankingDetailsResponse.model_validate(banking_detail)

        except Exception as e:
            raise e

