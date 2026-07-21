from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field


class Employer(SQLModel, table=True):
    __tablename__ = "employers"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    name: str = Field(nullable=False, index=True)
    address: str | None = Field(default=None, nullable=True)
    bin: str | None = Field(default=None, unique=True, index=True, nullable=True)  # Business Identification Number
    contact_email: str | None = Field(default=None, nullable=True)
    contact_phone: str | None = Field(default=None, nullable=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
