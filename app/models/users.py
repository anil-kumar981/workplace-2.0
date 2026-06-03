from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=False, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role")

    personal_details = relationship(
        "UserPersonalDetails",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    banking_details = relationship(
        "BankingDetails",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    created_announcements = relationship(
        "Announcement",
        back_populates="created_by",
        foreign_keys="Announcement.created_by_id",
    )

    updated_announcements = relationship(
        "Announcement",
        back_populates="updated_by",
        foreign_keys="Announcement.updated_by_id",
    )

    def __repr__(self) -> str:
        return f"<Employee id={self.id} name='{self.username}' email='{self.email}'>"
