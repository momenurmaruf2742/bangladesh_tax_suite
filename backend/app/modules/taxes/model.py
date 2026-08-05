import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


class TaxCalculation(SQLModel, table=True):
    __tablename__ = "tax_calculations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    employee_id: uuid.UUID = Field(
        foreign_key="employees.id", index=True, nullable=False
    )
    financial_year: str = Field(
        nullable=False, index=True, description="Financial year, e.g. 2025-2026"
    )
    total_salary: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    exempted_salary: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    taxable_salary: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    other_income: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    total_taxable_income: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    gross_tax: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    total_invested: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    eligible_investment: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    investment_rebate: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    minimum_tax: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    net_tax: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    ait_paid: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    tds_salary: Decimal = Field(default=Decimal("0.0"), max_digits=12, decimal_places=2)
    final_payable: Decimal = Field(
        default=Decimal("0.0"), max_digits=12, decimal_places=2
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )


class TaxRule(SQLModel, table=True):
    __tablename__ = "tax_rules"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    financial_year: str = Field(
        unique=True,
        index=True,
        nullable=False,
        description="Financial year, e.g. 2025-2026",
    )
    exemption_rate: Decimal = Field(
        default=Decimal("3.0"), max_digits=5, decimal_places=2
    )
    exemption_max: Decimal = Field(
        default=Decimal("450000.00"), max_digits=12, decimal_places=2
    )
    dps_max: Decimal = Field(
        default=Decimal("120000.00"), max_digits=12, decimal_places=2
    )
    rebate_rate: Decimal = Field(
        default=Decimal("0.15"), max_digits=5, decimal_places=2
    )
    income_rebate_limit_rate: Decimal = Field(
        default=Decimal("0.03"), max_digits=5, decimal_places=2
    )
    max_rebate_cap: Decimal = Field(
        default=Decimal("1000000.00"), max_digits=12, decimal_places=2
    )
    max_eligible_invest_rate: Decimal = Field(
        default=Decimal("0.20"), max_digits=5, decimal_places=2
    )
    max_eligible_invest_cap: Decimal = Field(
        default=Decimal("6666666.67"), max_digits=12, decimal_places=2
    )

    # JSON fields for thresholds, slabs, minimum_tax
    thresholds: dict = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    slabs: list = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    minimum_tax_location_based: bool = Field(default=True, nullable=False)
    minimum_tax: dict = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
