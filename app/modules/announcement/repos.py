from sqlalchemy import select

from app.models import Announcement
from app.schema import AnnouncementCreate, AnnouncementUpdate
from app.shared.base_repo import BaseRepo

from .interfaces.annoument_repo_interface import IAnnouncementRepo


class AnnouncementRepo(BaseRepo, IAnnouncementRepo):
    async def create_announcement_repo(
        self, created_by_id: int, announcement: AnnouncementCreate
    ) -> Announcement:
        try:
            new_announcement = Announcement(
                title=announcement.title,
                description=announcement.description,
                created_by_id=created_by_id,
            )
            self.db.add(new_announcement)
            await self.db.commit()
            await self.db.refresh(new_announcement)
            return new_announcement
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_all_announcements_repo(self) -> list[Announcement]:
        return await self.db.execute(select(Announcement)).scalars().all()

    async def get_announcement_by_id_repo(
        self, announcement_id: int
    ) -> Announcement | None:
        result = await self.db.execute(
            select(Announcement).where(Announcement.id == announcement_id)
        )
        return result.scalars().first()

    async def update_announcement_repo(
        self,
        announcement_id: int,
        updated_by_id: int,
        announcement: AnnouncementUpdate,
    ) -> Announcement | None:
        try:
            db_announcement = await self.get_announcement_by_id_repo(announcement_id)
            if db_announcement is None:
                return None

            # Extract updated attributes and set them on the loaded object
            update_data = announcement.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_announcement, key, value)

            db_announcement.updated_by_id = updated_by_id
            await self.db.commit()
            await self.db.refresh(db_announcement)
            return db_announcement
        except Exception as e:
            await self.db.rollback()
            raise e

    async def delete_announcement_repo(self, announcement_id: int) -> bool | None:
        try:
            db_announcement = await self.get_announcement_by_id_repo(announcement_id)
            if db_announcement is None:
                return None
            await self.db.delete(db_announcement)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise e
