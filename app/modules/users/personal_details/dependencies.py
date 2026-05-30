from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.sessions import get_db
from .interfaces.personal_details_repo_interface import IPersonalDetailsRepo
from .repos import PersonalDetailsRepo
from .interfaces.personal_details_service_interface import IPersonalDetailsService
from .services import UserPersonalDetailService
from app.modules.users.interfaces.user_service_interface import IUserService
from app.modules.users.dependencies import get_user_service

def get_personal_details_repo (db: AsyncSession = Depends(get_db)) -> IPersonalDetailsRepo:
    return PersonalDetailsRepo(db)

def get_personal_details_service(repo: IPersonalDetailsRepo = Depends(get_personal_details_repo), user_service: IUserService =  Depends(get_user_service)) -> IPersonalDetailsService:
    return UserPersonalDetailService(repo, user_service)