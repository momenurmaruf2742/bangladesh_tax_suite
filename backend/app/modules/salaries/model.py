from datetime import datetime, timezone
from decimal import Decimal
import uuid
from sqlmodel import SQLModel, Field


class SalarySlip(SQLModel, table=True):
    __tablename__ = "salary_slips"

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
    month: str = Field(
        nullable=False,
        index=True,
        description="Month in YYYY-MM format, e.g. 2025-07"
    )
    basic_salary: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    house_rent: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    medical_allowance: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    conveyance: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    festival_bonus: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    provident_fund: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2,
        description="Employee contribution to RPF"
    )
    employer_provident_fund: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2,
        description="Employer contribution to RPF"
    )
    other_allowances: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    tax_deducted: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2,
        description="Monthly source tax deducted (TDS)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SalaryCertificate(SQLModel, table=True):
    __tablename__ = "salary_certificates"

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
    file_path: str = Field(nullable=False, description="Local path to uploaded PDF")
    file_name: str = Field(nullable=False, description="Original name of the uploaded PDF")
    status: str = Field(default="Pending", nullable=False, description="Pending, Verified, Rejected")
    
    # Auto-extracted or manually corrected component totals
    total_basic: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    total_house_rent: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    total_medical: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    total_conveyance: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    total_bonus: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    total_provident_fund: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    total_tax_deducted: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    total_others: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
