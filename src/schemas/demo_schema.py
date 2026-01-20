import re
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, field_validator

from src.schemas.base_schema import BaseSchema
from src.utils.constant import BD_PHONE_REGEX


class DemoUserBase(BaseSchema):
    email: Optional[EmailStr] = Field(
        description="Email of user", examples=["abc@domin.com"]
    )
    name: str = Field(description="Name of user", min_length=1, max_length=255)
    contact_number: Optional[str] = Field(
        description="User contact number", examples=["01789987121"]
    )
    age: Optional[int] = Field(description="Age of user", ge=18)

    @field_validator("contact_number")
    @classmethod
    def validate_bd_phone(cls, value: str) -> str:
        if not re.match(BD_PHONE_REGEX, value):
            raise ValueError(
                "Invalid Bangladesh phone number. Use format: +8801XXXXXXXXX or 01XXXXXXXXX"
            )
        return value


class DemoUserCreate(DemoUserBase):
    email: EmailStr = Field(description="Email of user", examples=["abc@domin.com"])
    name: str = Field(description="Name of user", min_length=1, max_length=255)
    age: int = Field(description="Age of user", ge=18)


class DemoUserUpdate(DemoUserBase):
    pass


class DemoUserRecord(DemoUserBase):
    id: int = Field(description="ID of user", examples=[1, 2])
    created_at: datetime = Field(
        description="Date of user", examples=[datetime(2020, 1, 2)]
    )
