from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base

class OtpVerification(Base):
    __tablename__ = 'otp_verifications'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    otp_type = Column(String, nullable=False)  # 'login' or 'forgot_password'
    is_verified = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
