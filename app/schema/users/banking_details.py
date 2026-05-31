import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BankingDetailsBase(BaseModel):
    account_number: str = Field(
        ...,
        min_length=9,
        max_length=18,
        pattern=r"^\d+$",
        description="Bank account number (9 to 18 digits, numbers only)",
    )
    bank_name: str = Field(
        ..., min_length=2, max_length=100, description="Name of the bank"
    )
    branch_name: str = Field(
        ..., min_length=2, max_length=100, description="Name of the branch"
    )
    ifsc_code: str = Field(
        ...,
        pattern=r"^[A-Z]{4}0[a-zA-Z0-9]{6}$",
        description="11-character Indian Financial System Code (IFSC), e.g. HDFC0001234",
    )
    account_holder_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[a-zA-Z\s.]+$",
        description="Full name of the account holder (letters, spaces, and periods only)",
    )

    @field_validator("ifsc_code")
    @classmethod
    def format_ifsc_code(cls, v: str) -> str:
        """Ensure IFSC code is always stripped and in uppercase."""
        v = v.strip().upper()
        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", v):
            raise ValueError(
                "Invalid IFSC code format. It must be 11 characters (e.g. HDFC0001234)."
            )
        return v

    @field_validator(
        "account_number", "bank_name", "branch_name", "account_holder_name"
    )
    @classmethod
    def clean_strings(cls, v: str) -> str:
        """Strip leading and trailing whitespaces from string inputs."""
        return v.strip() if v else v


class BankingDetailsCreate(BankingDetailsBase):
    pass


class BankingDetailsUpdate(BaseModel):
    account_number: str | None = Field(
        None,
        min_length=9,
        max_length=18,
        pattern=r"^\d+$",
        description="Bank account number (9 to 18 digits, numbers only)",
    )
    bank_name: str | None = Field(
        None, min_length=2, max_length=100, description="Name of the bank"
    )
    branch_name: str | None = Field(
        None, min_length=2, max_length=100, description="Name of the branch"
    )
    ifsc_code: str | None = Field(
        None,
        pattern=r"^[A-Z]{4}0[a-zA-Z0-9]{6}$",
        description="11-character Indian Financial System Code (IFSC)",
    )
    account_holder_name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        pattern=r"^[a-zA-Z\s.]+$",
        description="Full name of the account holder",
    )

    @field_validator("ifsc_code")
    @classmethod
    def format_ifsc_code(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().upper()
        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", v):
            raise ValueError(
                "Invalid IFSC code format. It must be 11 characters (e.g. HDFC0001234)."
            )
        return v

    @field_validator(
        "account_number", "bank_name", "branch_name", "account_holder_name"
    )
    @classmethod
    def clean_strings(cls, v: str | None) -> str | None:
        return v.strip() if v else v


class BankingDetailsResponse(BankingDetailsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


BankingDetailsCreate = BankingDetailsCreate
BankingDetailsResponse = BankingDetailsResponse
BankingDetailsUpdate = BankingDetailsUpdate
