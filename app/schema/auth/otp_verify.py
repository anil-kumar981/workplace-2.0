from pydantic import BaseModel, EmailStr, Field
from .otp_request import OtpType

class OtpVerify(BaseModel):
    email: EmailStr
    otp_type: OtpType
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
