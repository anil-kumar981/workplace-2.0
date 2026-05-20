from fastapi import APIRouter, Depends, status
from app.schema import UserCreate
from app.services.user_service import UserService
from app.dependencies.user_dependencies import get_user_service
from app.shared.api_response.api_response import ApiResponse
from app.shared.exceptions import AppException

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    """
    Creates a new user account, securing their credentials and registering them in the system.
    """
    new_user = await service.create_user_service(user_in)
    return ApiResponse.success(
        data=new_user,
        message="User created successfully",
        code=status.HTTP_201_CREATED,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_users(service: UserService = Depends(get_user_service)):
    """
    Retrieves all registered user accounts.
    """
    users = await service.get_all_users_service()
    return ApiResponse.success(
        data=users, message="Successfully retrieved list of all registered users."
    )


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int, service: UserService = Depends(get_user_service)
):
    """
    Finds a single user account by its unique integer identifier.
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
