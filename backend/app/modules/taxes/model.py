from datetime import datetime, timezone
from decimal import Decimal
import uuid
from sqlmodel import SQLModel, Field


class TaxCalculation(SQLModel, table=True):
    __tablename__ = "tax_calculations"

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
    total_salary: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    exempted_salary: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    taxable_salary: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    other_income: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    total_taxable_income: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    gross_tax: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    total_invested: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    eligible_investment: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    investment_rebate: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    minimum_tax: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    net_tax: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    ait_paid: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    tds_salary: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    final_payable: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=12,
        decimal_places=2
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
