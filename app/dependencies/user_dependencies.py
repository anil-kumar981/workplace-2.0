from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.get_db import get_db
from app.repos.user_repo import UserRepo
from app.services.user_service import UserService

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepo:
    """
    Dependency provider to instantiate UserRepo with an active DB session.
    """
    return UserRepo(db)

def get_user_service(repo: UserRepo = Depends(get_user_repo)) -> UserService:
    """
    Dependency provider to instantiate UserService with the UserRepo.
    """
    return UserService(repo)
