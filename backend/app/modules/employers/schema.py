from datetime import datetime
import uuid
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class EmployerBase(BaseModel):
    name: str = Field(..., min_length=2, description="Name of the employer company")
    address: str | None = Field(None, description="Physical address of the company")
    bin: str | None = Field(None, description="9 or 13-digit Business Identification Number (BIN)")
    contact_email: EmailStr | None = Field(None, description="Primary contact email")
    contact_phone: str | None = Field(None, description="Primary contact phone number")


class EmployerCreate(EmployerBase):
    pass


class EmployerUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    bin: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None


class EmployerResponse(EmployerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
