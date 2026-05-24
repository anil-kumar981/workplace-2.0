from enum import Enum
from pydantic import BaseModel, EmailStr

class OtpType(str, Enum):
    register = "register"
    login = "login"
    forgot_password = "forgot_password"

class OtpRequest(BaseModel):
    email: EmailStr
    otp_type: OtpType
