from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text, func
from sqlalchemy.orm import relationship
from app.enums import Gender, MaritalStatus

class UserPersonalDetails(Base):
    __tablename__ = "user_personal_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    personal_mail = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    gender = Column(Enum(Gender))
    date_of_birth = Column(Date)
    nationality = Column(String(100))
    marital_status = Column(Enum(MaritalStatus))
    pan_card = Column(String(20), nullable=False)
    emergency_number = Column(String(20), nullable=False)
    disability = Column(String(100))
    blood_group = Column(String(10))
    medical_history = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relational mapping
    user = relationship("User", back_populates="personal_details")
    
    
    
    