from .services import UserPersonalDetailService
from .repos import PersonalDetailsRepo
from .interfaces.personal_details_service_interface import IPersonalDetailsService
from .interfaces.personal_details_repo_interface import IPersonalDetailsRepo
from .router import router as personal_details_router

__all__ = [
    "UserPersonalDetailService",
    "PersonalDetailsRepo",
    "IPersonalDetailsService",
    "IPersonalDetailsRepo",
    "personal_details_router",
]