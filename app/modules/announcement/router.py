from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user
from app.schema import AnnouncementCreate, AnnouncementUpdate
from app.shared.api_response.api_response import ApiResponse
from app.shared.utils.check_permissions import PermissionChecker

from .dependencies import get_announcement_service
from .interfaces.announcement_services_interface import IAnnouncementService

router = APIRouter(
    prefix="/announcements",
    tags=["Announcements"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("Announcement", "manage"))],
)
async def create_announcement(
    announcement: AnnouncementCreate,
    current_user=Depends(get_current_user),
    service: IAnnouncementService = Depends(get_announcement_service),
):
    """
    Creates a new announcement.
    """
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", current_user)
    result = await service.create_announcement_service(announcement, current_user.id)
    return ApiResponse.success(data=result, message="Announcement created successfully")


@router.get("/", dependencies=[Depends(PermissionChecker("Announcement", "view"))])
async def get_all_announcements(
    service: IAnnouncementService = Depends(get_announcement_service),
):
    """
    Gets all announcements.
    """
    result = await service.get_all_announcements_service()
    return ApiResponse.success(
        data=result, message="Announcements fetched successfully"
    )


@router.get(
    "/{announcement_id}",
    dependencies=[Depends(PermissionChecker("Announcement", "view"))],
)
async def get_announcement_by_id(
    announcement_id: int,
    service: IAnnouncementService = Depends(get_announcement_service),
):
    """
    Gets an announcement by ID.
    """
    result = await service.get_announcement_by_id_service(announcement_id)
    return ApiResponse.success(data=result, message="Announcement fetched successfully")


@router.patch(
    "/{announcement_id}",
    dependencies=[Depends(PermissionChecker("Announcement", "manage"))],
)
async def update_announcement(
    announcement_id: int,
    announcement: AnnouncementUpdate,
    current_user=Depends(get_current_user),
    service: IAnnouncementService = Depends(get_announcement_service),
):
    """
    Updates an announcement.
    """
    result = await service.update_announcement_service(
        announcement_id, announcement, current_user.id
    )
    return ApiResponse.success(data=result, message="Announcement updated successfully")


@router.delete(
    "/{announcement_id}",
    dependencies=[Depends(PermissionChecker("Announcement", "manage"))],
)
async def delete_announcement(
    announcement_id: int,
    service: IAnnouncementService = Depends(get_announcement_service),
):
    """
    Deletes an announcement.
    """
    result = await service.delete_announcement_service(announcement_id)
    return ApiResponse.success(data=result, message="Announcement deleted successfully")
