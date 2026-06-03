from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[str] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    created_by = relationship(
        "User", foreign_keys=[created_by_id], back_populates="created_announcements"
    )
    updated_by = relationship(
        "User", foreign_keys=[updated_by_id], back_populates="updated_announcements"
    )
