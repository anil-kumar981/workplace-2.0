from app.schema import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate
from app.shared.base_service import BaseService

from .interfaces.annoument_repo_interface import IAnnouncementRepo
from .interfaces.announcement_services_interface import IAnnouncementService


class AnnouncementService(BaseService[IAnnouncementRepo], IAnnouncementService):
    async def create_announcement_service(
        self, announcement: AnnouncementCreate, created_by_id: int
    ) -> AnnouncementResponse:
        try:
            result = await self.repo.create_announcement_repo(
                created_by_id, announcement
            )
            return AnnouncementResponse.model_validate(result)
        except Exception as e:
            raise e

    async def get_all_announcements_service(self) -> list[AnnouncementResponse]:
        result = await self.repo.get_all_announcements_repo()
        return [AnnouncementResponse.model_validate(r) for r in result]

    async def get_announcement_by_id_service(
        self, announcement_id: int
    ) -> AnnouncementResponse | None:
        result = await self.repo.get_announcement_by_id_repo(announcement_id)
        if result is None:
            return None
        return AnnouncementResponse.model_validate(result)

    async def update_announcement_service(
        self, announcement_id: int, announcement: AnnouncementUpdate, updated_by_id: int
    ) -> AnnouncementResponse | None:
        try:
            result = await self.repo.update_announcement_repo(
                announcement_id, updated_by_id, announcement
            )
            if result is None:
                return None
            return AnnouncementResponse.model_validate(result)
        except Exception as e:
            raise e

    async def delete_announcement_service(self, announcement_id: int) -> bool | None:
        try:
            result = await self.repo.delete_announcement_repo(announcement_id)
            return result
        except Exception as e:
            raise e
