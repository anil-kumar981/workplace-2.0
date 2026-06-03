from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.sessions import get_db

from .interfaces.annoument_repo_interface import IAnnouncementRepo
from .interfaces.announcement_services_interface import IAnnouncementService
from .repos import AnnouncementRepo
from .services import AnnouncementService


def get_announcement_repo(db: AsyncSession = Depends(get_db)) -> IAnnouncementRepo:
    return AnnouncementRepo(db)


def get_announcement_service(
    repo: IAnnouncementRepo = Depends(get_announcement_repo),
) -> IAnnouncementService:
    return AnnouncementService(repo)
