from abc import ABC, abstractmethod

from app.schema import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate


class IAnnouncementService(ABC):
    @abstractmethod
    async def create_announcement_service(
        self, announcement: AnnouncementCreate, created_by_id: int
    ) -> AnnouncementResponse:
        pass

    @abstractmethod
    async def get_all_announcements_service(self) -> list[AnnouncementResponse]:
        pass

    @abstractmethod
    async def get_announcement_by_id_service(
        self, announcement_id: int
    ) -> AnnouncementResponse | None:
        pass

    @abstractmethod
    async def update_announcement_service(
        self, announcement_id: int, announcement: AnnouncementUpdate, updated_by_id: int
    ) -> AnnouncementResponse | None:
        pass

    @abstractmethod
    async def delete_announcement_service(self, announcement_id: int) -> bool | None:
        pass
