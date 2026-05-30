from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.enums import Gender, MaritalStatus

class UserPersonalDetailBase(BaseModel):
    personal_mail: EmailStr = Field(..., max_length=100)
    phone_number: str = Field(..., max_length=20)
    gender: Gender | None = None
    date_of_birth: date | None = None
    nationality: str | None = Field(None, max_length=100)
    marital_status: MaritalStatus | None = None
    pan_card: str = Field(..., max_length=20)
    emergency_number: str = Field(..., max_length=20)
    disability: str | None = Field(None, max_length=100)
    blood_group: str | None = Field(None, max_length=10)
    medical_history: str | None = None

class UserPersonalDetailCreate(UserPersonalDetailBase):
    pass

class UserPersonalDetailUpdate(BaseModel):
    personal_mail: EmailStr | None = Field(None, max_length=100)
    phone_number: str | None = Field(None, max_length=20)
    gender: Gender | None = None
    date_of_birth: date | None = None
    nationality: str | None = Field(None, max_length=100)
    marital_status: MaritalStatus | None = None
    pan_card: str | None = Field(None, max_length=20)
    emergency_number: str | None = Field(None, max_length=20)
    disability: str | None = Field(None, max_length=100)
    blood_group: str | None = Field(None, max_length=10)
    medical_history: str | None = None

class UserPersonalDetailResponse(UserPersonalDetailBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Support plural naming conventions transparently
UserPersonalDetailsCreate = UserPersonalDetailCreate
UserPersonalDetailsUpdate = UserPersonalDetailUpdate
UserPersonalDetailsResponse = UserPersonalDetailResponse
