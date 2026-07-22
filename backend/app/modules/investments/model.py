from datetime import datetime, timezone, date as py_date
from decimal import Decimal
import uuid
from sqlmodel import SQLModel, Field


class Investment(SQLModel, table=True):
    __tablename__ = "investments"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    employee_id: uuid.UUID = Field(
        foreign_key="employees.id",
        index=True,
        nullable=False
    )
    financial_year: str = Field(
        nullable=False,
        index=True,
        description="Financial year, e.g. 2025-2026"
    )
    category: str = Field(
        nullable=False,
        description="DPS, Life Insurance, Sanchayapatra, Stock Market, or Other"
    )
    amount: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    description: str | None = Field(default=None, nullable=True)
    doc_path: str | None = Field(default=None, nullable=True, description="Path to proof of investment")
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )


class AITRecord(SQLModel, table=True):
    __tablename__ = "ait_records"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    employee_id: uuid.UUID = Field(
        foreign_key="employees.id",
        index=True,
        nullable=False
    )
    financial_year: str = Field(
        nullable=False,
        index=True,
        description="Financial year, e.g. 2025-2026"
    )
    category: str = Field(
        nullable=False,
        description="Car Registration, Bank Interest TDS, Property Transaction, or Other"
    )
    amount: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    challan_number: str | None = Field(default=None, nullable=True)
    challan_date: py_date | None = Field(default=None, nullable=True)
    description: str | None = Field(default=None, nullable=True)
    doc_path: str | None = Field(default=None, nullable=True, description="Path to AIT payment receipt")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
