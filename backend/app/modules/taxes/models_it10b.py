import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlmodel import Column, Field, JSON, SQLModel


class IT10BStatement(SQLModel, table=True):
    """
    NBR Form IT-10B (2023) - Statement of Assets, Liabilities, and Net Wealth.
    Enforces statutory double-entry reconciliation:
    Sources of Fund + Previous Year Net Wealth = Lifestyle Outflow + Closing Net Wealth + Liabilities
    Difference = Total Fund Inflow - (Change in Net Wealth + Lifestyle Expenses + Other Outflow) = 0
    """
    __tablename__ = "it10b_statements"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id", index=True, nullable=False
    )
    financial_year: str = Field(
        nullable=False, index=True, description="Financial year, e.g. 2025-2026"
    )
    assessment_year: str = Field(
        nullable=False, description="Assessment year, e.g. 2026-2027"
    )

    # 1. Source of Fund (Inflow)
    taxable_income: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    tax_exempted_income: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    gifts_and_other_receipts: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    total_fund_inflow: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)

    # 2. Previous Year Wealth
    net_wealth_previous_year: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)

    # 3. Outflow
    lifestyle_expenses: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    other_outflow_losses: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    total_fund_outflow: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)

    # 4. Assets Breakdown
    business_assets: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    non_agricultural_property: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    agricultural_property: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    financial_assets_dps: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    financial_assets_others: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    motor_vehicles_value: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    ornaments_gold_value: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    furniture_electronics_value: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    cash_in_hand: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    bank_balances: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    other_deposits: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)

    # 5. Liabilities
    institutional_liabilities: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    non_institutional_liabilities: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    total_liabilities: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)

    # 6. Computed Reconciliation Checks
    gross_wealth: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    net_wealth_closing: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    change_in_net_wealth: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    difference: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    is_balanced: bool = Field(default=False, nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


class IT10BAssetItem(SQLModel, table=True):
    """
    NBR IT-10B Detailed Asset Line Item.
    Supports Gift / Inheritance acquisitions with financial cost = 0.00
    while preserving physical specifications (e.g. Engine CC, Gold gram/bhori).
    """
    __tablename__ = "it10b_asset_items"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    statement_id: uuid.UUID = Field(
        foreign_key="it10b_statements.id", index=True, nullable=False
    )
    asset_category: str = Field(
        index=True,
        nullable=False,
        description="motor_vehicles, ornaments_gold, non_agricultural_property, agricultural_property, etc."
    )
    description: str = Field(
        nullable=False,
        description="e.g. Dhaka Metro LA 67-6774 Motorcycle 155 CC, Gold 4.75 Gram"
    )
    acquisition_type: str = Field(
        default="Purchase",
        nullable=False,
        description="Purchase, Gift, Inheritance"
    )
    cost_value: Decimal = Field(
        default=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
        description="Financial cost value (can be 0.00 for Gift / Inheritance)"
    )
    particulars: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Physical metadata: CC, Gram, Bhori, Reg Number, Engine Number, Location, etc."
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


class LifestyleExpense(SQLModel, table=True):
    """
    NBR Form IT-10BB (2023) - Statement of Expenses Relating to Lifestyle.
    Tracks the 9 mandatory categorized expenditure lines under Income Tax Act 2023.
    """
    __tablename__ = "lifestyle_expenses"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id", index=True, nullable=False
    )
    financial_year: str = Field(
        nullable=False, index=True, description="Financial year, e.g. 2025-2026"
    )
    assessment_year: str = Field(
        nullable=False, description="Assessment year, e.g. 2026-2027"
    )

    # Line 1: Personal & family fooding, clothing, essentials
    fooding_clothing_essentials: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Line 2: Housing expense
    housing_expense: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Line 3: Personal transport expense
    transport_expense: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Line 4: Utility expense (Electricity, Gas, Water, Internet, Phone)
    utility_expense: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Line 5: Education expenses
    education_expenses: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Line 6: Personal local/foreign travel & vacation
    travel_vacation_expenses: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Line 7: Festival and other special expenses
    festival_special_expenses: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Line 8: Tax Deducted / Collected at Source & Advance Tax
    tax_deducted_source_advance: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Line 9: Interest paid on personal borrowing
    interest_paid_borrowing: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    # Additional / Miscellaneous expenses
    other_expenses: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )

    # Total Lifestyle Outflow (Sum of lines 1 to 9 + other)
    total_lifestyle_expense: Decimal = Field(
        default=Decimal("0.00"), max_digits=14, decimal_places=2
    )
    auto_synced_tds: bool = Field(
        default=True,
        nullable=False,
        description="Whether line 8 is automatically synced from Salary TDS & AIT ledger"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
