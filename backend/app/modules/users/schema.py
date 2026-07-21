from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., description="Phone number, e.g. +8801700000000")
    first_name: str
    last_name: str
    tin: str | None = Field(None, description="12-digit TAX Identification Number (TIN)")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    tin: str | None = None
    password: str | None = Field(None, min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    tin: str | None
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime
