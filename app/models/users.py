from sqlalchemy import Column,ForeignKey, Integer, String, Boolean, DateTime, func
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=False, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role")

    personal_details = relationship(
        'UserPersonalDetails',
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False 
    )
