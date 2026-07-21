from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    email: str = Field(unique=True, index=True, nullable=False)
    phone: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    tin: str | None = Field(default=None, unique=True, index=True, nullable=True)
    is_active: bool = Field(default=True, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    role: str = Field(default="Employee", nullable=False)  # Admin, CA, Employee
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
