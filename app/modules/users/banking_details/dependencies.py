from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.sessions import get_db
from app.modules.users.dependencies import get_user_service
from app.modules.users.interfaces.user_service_interface import IUserService

from .interfaces.banking_details_repo_interface import IBankingDetailsRepo
from .interfaces.banking_details_service_interface import IBankingDetailsService
from .repos import BankingDetailsRepo
from .services import BankingDetailsService


def get_banking_details_repo(db: AsyncSession = Depends(get_db)) -> IBankingDetailsRepo:
    return BankingDetailsRepo(db)


def get_banking_details_service(
    repo: IBankingDetailsRepo = Depends(get_banking_details_repo),
    user_service: IUserService = Depends(get_user_service),
) -> IBankingDetailsService:
    return BankingDetailsService(repo, user_service)
