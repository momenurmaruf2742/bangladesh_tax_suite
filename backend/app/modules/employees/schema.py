from datetime import datetime, date
import uuid
from pydantic import BaseModel, Field, ConfigDict
from app.modules.users.schema import UserResponse
from app.modules.employers.schema import EmployerResponse


class EmployeeBase(BaseModel):
    employer_id: uuid.UUID | None = Field(None, description="Linked employer company ID")
    designation: str | None = Field(None, description="Job designation, e.g. Software Engineer")
    department: str | None = Field(None, description="Department, e.g. Engineering")
    date_of_joining: date | None = Field(None, description="Date of joining the company")
    nid: str | None = Field(None, description="10 or 17-digit National Identification Number (NID)")
    tax_zone: str | None = Field(None, description="Bangladesh tax zone, e.g. Tax Zone 15, Dhaka")
    tax_circle: str | None = Field(None, description="Bangladesh tax circle, e.g. Circle 302")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employer_id: uuid.UUID | None = None
    designation: str | None = None
    department: str | None = None
    date_of_joining: date | None = None
    nid: str | None = None
    tax_zone: str | None = None
    tax_circle: str | None = None


class EmployeeResponse(EmployeeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeDetailedResponse(EmployeeResponse):
    user: UserResponse
    employer: EmployerResponse | None = None

    model_config = ConfigDict(from_attributes=True)
