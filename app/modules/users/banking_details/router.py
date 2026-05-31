from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user
from app.schema import BankingDetailsCreate, BankingDetailsUpdate
from app.shared.api_response.api_response import ApiResponse
from app.shared.utils.check_permissions import PermissionChecker

from .dependencies import get_banking_details_service
from .interfaces.banking_details_service_interface import IBankingDetailsService

router = APIRouter(
    prefix="/user/banking-details",
    tags=["user_banking_details"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("User", "ManageStaff"))],
)
async def create_banking_details(
    banking_details: BankingDetailsCreate,
    user_id: int,
    service: IBankingDetailsService = Depends(get_banking_details_service),
):
    result = await service.create_banking_details(user_id, banking_details)
    return ApiResponse.success(
        data=result,
        message="Banking details created successfully",
        code=status.HTTP_201_CREATED,
    )


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("User", "View"))],
)
async def get_banking_details(
    user_id: int,
    service: IBankingDetailsService = Depends(get_banking_details_service),
):
    result = await service.get_banking_details(user_id)
    return ApiResponse.success(
        data=result,
        message="Banking details retrieved successfully",
        code=status.HTTP_200_OK,
    )


@router.patch(
    "/update/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("User", "ManageStaff"))],
)
async def update_banking_details(
    user_id: int,
    update_details: BankingDetailsUpdate,
    service: IBankingDetailsService = Depends(get_banking_details_service),
):
    result = await service.update_banking_details(user_id, update_details)
    return ApiResponse.success(
        data=result,
        message="Banking details updated successfully",
        code=status.HTTP_200_OK,
    )

