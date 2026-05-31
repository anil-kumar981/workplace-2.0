from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user
from app.schema import UserPersonalDetailCreate, UserPersonalDetailUpdate
from app.shared.api_response.api_response import ApiResponse
from app.shared.utils.check_permissions import PermissionChecker

from .dependencies import get_personal_details_service
from .interfaces.personal_details_service_interface import IPersonalDetailsService

router = APIRouter(
    prefix="/users/personal-details",
    tags=["User Personal Details"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("User", "ManageStaff"))],
)
async def create_personal_details(
    user_id: int,
    create_details: UserPersonalDetailCreate,
    service: IPersonalDetailsService = Depends(get_personal_details_service),
):
    new_details = await service.create_personal_details(create_details, user_id)
    return ApiResponse.success(
        data=new_details,
        message="Personal details created successfully",
        code=status.HTTP_201_CREATED,
    )


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("User", "view"))],
)
async def get_personal_details(
    user_id: int,
    service: IPersonalDetailsService = Depends(get_personal_details_service),
):
    details = await service.get_personal_details(user_id)
    return ApiResponse.success(
        data=details,
        message="Personal details retrieved successfully",
        code=status.HTTP_200_OK,
    )


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("User", "ManageStaff"))],
)
async def update_personal_details(
    user_id: int,
    update_details: UserPersonalDetailUpdate,
    service: IPersonalDetailsService = Depends(get_personal_details_service),
):
    details = await service.update_personal_details(update_details, user_id)
    return ApiResponse.success(
        data=details,
        message="Personal details updated successfully",
        code=status.HTTP_200_OK,
    )
