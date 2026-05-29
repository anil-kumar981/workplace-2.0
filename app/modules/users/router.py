from fastapi import APIRouter, Depends, status
from app.schema import UserCreate
from app.shared.api_response.api_response import ApiResponse
from app.shared.exceptions import AppException
from app.shared.utils.check_permissions import PermissionChecker
from app.modules.auth.dependencies import get_current_user
from .interfaces.user_service_interface import IUserService
from .dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user)])


@router.post(
    "/create", 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("User", "ManageStaff"))]
)
async def create_user(
    user_in: UserCreate, service: IUserService = Depends(get_user_service)
):
    """
    Creates a new user account, securing their credentials and registering them in the system.
    Requires 'ManageStaff' action on 'User' resource.
    """
    new_user = await service.create_user_service(user_in)
    return ApiResponse.success(
        data=new_user,
        message="User created successfully",
        code=status.HTTP_201_CREATED,
    )


@router.get(
    "/", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("User", "view"))]
)
async def get_all_users(service: IUserService = Depends(get_user_service)):
    """
    Retrieves all registered user accounts.
    Requires 'view' action on 'User' resource.
    """
    users = await service.get_all_users_service()
    return ApiResponse.success(
        data=users, message="Successfully retrieved list of all registered users."
    )


@router.get(
    "/{user_id}", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("User", "view"))]
)
async def get_user_by_id(
    user_id: int, service: IUserService = Depends(get_user_service)
):
    """
    Finds a single user account by its unique integer identifier.
    Requires 'view' action on 'User' resource (either 'any' scope, or 'own' scope where user_id matches).
    """
    user = await service.get_user_by_id_service(user_id)
    if not user:
        raise AppException(
            message=f"No user account registered with unique identifier '{user_id}'",
            code=status.HTTP_404_NOT_FOUND,
        )
    return ApiResponse.success(
        data=user, message="Successfully retrieved requested user account."
    )
