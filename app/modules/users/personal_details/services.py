from app.modules.users.interfaces.user_service_interface import IUserService
from app.schema import (
    UserPersonalDetailCreate,
    UserPersonalDetailResponse,
    UserPersonalDetailUpdate,
)
from app.shared.exceptions import AppException

from .interfaces.personal_details_repo_interface import IPersonalDetailsRepo
from .interfaces.personal_details_service_interface import IPersonalDetailsService


class UserPersonalDetailService(IPersonalDetailsService):
    def __init__(self, repo: IPersonalDetailsRepo, user_service: IUserService):
        self.repo = repo
        self.user_service = user_service

    async def create_personal_details(
        self, personal_details: UserPersonalDetailCreate, user_id: int
    ) -> UserPersonalDetailResponse:
        try:
            user = await self.user_service.get_user_by_id_service(user_id)
            if not user:
                raise AppException("User not found", 404)
            personal_detail = await self.repo.create_personal_details(
                personal_details, user_id
            )
            return UserPersonalDetailResponse.model_validate(personal_detail)
        except Exception as e:
            raise e

    async def get_personal_details(
        self, user_id: int
    ) -> UserPersonalDetailResponse | None:
        try:
            user = await self.user_service.get_user_by_id_service(user_id)
            if not user:
                raise AppException("User not found", 404)
            personal_detail = await self.repo.get_personal_details(user_id)
            return UserPersonalDetailResponse.model_validate(personal_detail)
        except Exception as e:
            raise e

    async def update_personal_details(
        self, personal_details: UserPersonalDetailUpdate, user_id: int
    ) -> UserPersonalDetailResponse:
        try:
            user = await self.user_service.get_user_by_id_service(user_id)
            if not user:
                raise AppException("User not found", 404)

            check_exisiting_pd = await self.repo.get_personal_details(user_id)
            if not check_exisiting_pd:
                raise AppException("Personal Details not found for the provided user.")

            personal_detail = await self.repo.update_personal_details(
                personal_details, user_id
            )
            return UserPersonalDetailResponse.model_validate(personal_detail)

        except Exception as e:
            raise e
