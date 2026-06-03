from abc import ABC, abstractmethod

from app.models import Announcement
from app.schema import AnnouncementCreate, AnnouncementUpdate


class IAnnouncementRepo(ABC):
    @abstractmethod
    async def create_announcement_repo(
        self, created_by_id: int, announcement: AnnouncementCreate
    ) -> Announcement:
        pass

    @abstractmethod
    async def get_all_announcements_repo(self) -> list[Announcement]:
        pass

    @abstractmethod
    async def get_announcement_by_id_repo(
        self, announcement_id: int
    ) -> Announcement | None:
        pass

    @abstractmethod
    async def update_announcement_repo(
        self, announcement_id: int, updated_by_id: int, announcement: AnnouncementUpdate
    ) -> Announcement | None:
        pass

    @abstractmethod
    async def delete_announcement_repo(self, announcement_id: int) -> bool | None:
        pass
