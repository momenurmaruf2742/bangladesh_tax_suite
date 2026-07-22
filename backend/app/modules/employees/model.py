from datetime import datetime, timezone, date
import uuid
from sqlmodel import SQLModel, Field


class Employee(SQLModel, table=True):
    __tablename__ = "employees"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        unique=True,
        index=True,
        nullable=False
    )
    employer_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="employers.id",
        index=True,
        nullable=True
    )
    designation: str | None = Field(default=None, nullable=True)
    department: str | None = Field(default=None, nullable=True)
    date_of_joining: date | None = Field(default=None, nullable=True)
    nid: str | None = Field(default=None, unique=True, index=True, nullable=True)
    tax_zone: str | None = Field(default=None, nullable=True)
    tax_circle: str | None = Field(default=None, nullable=True)
    gender: str = Field(default="Male", nullable=False)
    is_disabled: bool = Field(default=False, nullable=False)
    is_freedom_fighter: bool = Field(default=False, nullable=False)
    location: str = Field(default="Dhaka/Chittagong City Corporation", nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
