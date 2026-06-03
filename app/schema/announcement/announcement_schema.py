from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseAnnouncement(BaseModel):
    title: str = Field(
        ..., min_length=2, max_length=100, description="Title of the announcement"
    )
    description: str = Field(
        ...,
        min_length=2,
        max_length=1000,
        description="Description of the announcement",
    )


class AnnouncementCreate(BaseAnnouncement):
    pass


class AnnouncementResponse(BaseAnnouncement):
    id: int
    created_by_id: int
    updated_by_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementUpdate(BaseAnnouncement):
    title: str | None = Field(
        None, min_length=2, max_length=100, description="Title of the announcement"
    )
    description: str | None = Field(
        None,
        min_length=2,
        max_length=1000,
        description="Description of the announcement",
    )


AnnouncementCreate = AnnouncementCreate
AnnouncementResponse = AnnouncementResponse
AnnouncementUpdate = AnnouncementUpdate
