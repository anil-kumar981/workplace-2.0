from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.sessions import get_db
from .interfaces.user_repo_interface import IUserRepo
from .repos import UserRepo
from .interfaces.user_service_interface import IUserService
from .services import UserService

def get_user_repo(db: AsyncSession = Depends(get_db)) -> IUserRepo:
    """
    Dependency provider to instantiate UserRepo with an active DB session.
    """
    return UserRepo(db)

def get_user_service(repo: IUserRepo = Depends(get_user_repo)) -> IUserService:
    """
    Dependency provider to instantiate UserService with the UserRepo.
    """
    return UserService(repo)
