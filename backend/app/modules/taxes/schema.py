import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TaxSlabBreakdown(BaseModel):
    slab_name: str
    tax_rate: float
    taxable_amount: Decimal
    tax_amount: Decimal


class TaxCalculationBase(BaseModel):
    financial_year: str = "2025-2026"
    other_income: Decimal = Decimal("0.0")


class TaxCalculationCreate(TaxCalculationBase):
    pass


class TaxCalculationResponse(TaxCalculationBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    total_salary: Decimal
    exempted_salary: Decimal
    taxable_salary: Decimal
    total_taxable_income: Decimal
    gross_tax: Decimal
    total_invested: Decimal
    eligible_investment: Decimal
    investment_rebate: Decimal
    minimum_tax: Decimal
    net_tax: Decimal
    ait_paid: Decimal
    tds_salary: Decimal
    final_payable: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaxDetailsResponse(BaseModel):
    summary: TaxCalculationResponse
    slabs: list[TaxSlabBreakdown]
    employee_gender: str
    employee_location: str
    is_disabled: bool
    is_freedom_fighter: bool


class TaxRuleBase(BaseModel):
    financial_year: str
    exemption_rate: Decimal = Decimal("3.0")
    exemption_max: Decimal = Decimal("450000.00")
    dps_max: Decimal = Decimal("120000.00")
    rebate_rate: Decimal = Decimal("0.15")
    income_rebate_limit_rate: Decimal = Decimal("0.03")
    max_rebate_cap: Decimal = Decimal("1000000.00")
    max_eligible_invest_rate: Decimal = Decimal("0.20")
    max_eligible_invest_cap: Decimal = Decimal("6666666.67")
    thresholds: dict
    slabs: list
    minimum_tax_location_based: bool = True
    minimum_tax: dict


class TaxRuleCreate(TaxRuleBase):
    pass


class TaxRuleUpdate(BaseModel):
    exemption_rate: Decimal | None = None
    exemption_max: Decimal | None = None
    dps_max: Decimal | None = None
    rebate_rate: Decimal | None = None
    income_rebate_limit_rate: Decimal | None = None
    max_rebate_cap: Decimal | None = None
    max_eligible_invest_rate: Decimal | None = None
    max_eligible_invest_cap: Decimal | None = None
    thresholds: dict | None = None
    slabs: list | None = None
    minimum_tax_location_based: bool | None = None
    minimum_tax: dict | None = None


class TaxRuleResponse(TaxRuleBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- IT-10BB Lifestyle Expenses Schemas ---


class LifestyleExpenseBase(BaseModel):
    financial_year: str = "2025-2026"
    assessment_year: str | None = None
    fooding_clothing_essentials: Decimal = Decimal("0.00")
    housing_expense: Decimal = Decimal("0.00")
    transport_expense: Decimal = Decimal("0.00")
    utility_expense: Decimal = Decimal("0.00")
    education_expenses: Decimal = Decimal("0.00")
    travel_vacation_expenses: Decimal = Decimal("0.00")
    festival_special_expenses: Decimal = Decimal("0.00")
    tax_deducted_source_advance: Decimal | None = None
    interest_paid_borrowing: Decimal = Decimal("0.00")
    other_expenses: Decimal = Decimal("0.00")
    auto_synced_tds: bool = True


class LifestyleExpenseCreate(LifestyleExpenseBase):
    pass


class LifestyleExpenseUpdate(BaseModel):
    assessment_year: str | None = None
    fooding_clothing_essentials: Decimal | None = None
    housing_expense: Decimal | None = None
    transport_expense: Decimal | None = None
    utility_expense: Decimal | None = None
    education_expenses: Decimal | None = None
    travel_vacation_expenses: Decimal | None = None
    festival_special_expenses: Decimal | None = None
    tax_deducted_source_advance: Decimal | None = None
    interest_paid_borrowing: Decimal | None = None
    other_expenses: Decimal | None = None
    auto_synced_tds: bool | None = None


class LifestyleExpenseResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    financial_year: str
    assessment_year: str
    fooding_clothing_essentials: Decimal
    housing_expense: Decimal
    transport_expense: Decimal
    utility_expense: Decimal
    education_expenses: Decimal
    travel_vacation_expenses: Decimal
    festival_special_expenses: Decimal
    tax_deducted_source_advance: Decimal
    interest_paid_borrowing: Decimal
    other_expenses: Decimal
    total_lifestyle_expense: Decimal
    auto_synced_tds: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- IT-10B Asset Item Schemas ---


class IT10BAssetItemBase(BaseModel):
    asset_category: str
    description: str
    acquisition_type: str = "Purchase"  # Purchase, Gift, Inheritance
    cost_value: Decimal = Decimal("0.00")
    particulars: dict = {}


class IT10BAssetItemCreate(IT10BAssetItemBase):
    pass


class IT10BAssetItemResponse(IT10BAssetItemBase):
    id: uuid.UUID
    statement_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- IT-10B Statement Schemas ---


class IT10BStatementBase(BaseModel):
    financial_year: str = "2025-2026"
    assessment_year: str | None = None

    # Source of Fund
    taxable_income: Decimal = Decimal("0.00")
    tax_exempted_income: Decimal = Decimal("0.00")
    gifts_and_other_receipts: Decimal = Decimal("0.00")

    # Previous Year Wealth
    net_wealth_previous_year: Decimal = Decimal("0.00")

    # Outflow
    lifestyle_expenses: Decimal | None = None
    other_outflow_losses: Decimal = Decimal("0.00")

    # Assets Breakdown
    business_assets: Decimal = Decimal("0.00")
    non_agricultural_property: Decimal = Decimal("0.00")
    agricultural_property: Decimal = Decimal("0.00")
    financial_assets_dps: Decimal = Decimal("0.00")
    financial_assets_others: Decimal = Decimal("0.00")
    motor_vehicles_value: Decimal = Decimal("0.00")
    ornaments_gold_value: Decimal = Decimal("0.00")
    furniture_electronics_value: Decimal = Decimal("0.00")
    cash_in_hand: Decimal = Decimal("0.00")
    bank_balances: Decimal = Decimal("0.00")
    other_deposits: Decimal = Decimal("0.00")

    # Liabilities
    institutional_liabilities: Decimal = Decimal("0.00")
    non_institutional_liabilities: Decimal = Decimal("0.00")


class IT10BStatementCreate(IT10BStatementBase):
    pass


class IT10BStatementUpdate(BaseModel):
    assessment_year: str | None = None
    taxable_income: Decimal | None = None
    tax_exempted_income: Decimal | None = None
    gifts_and_other_receipts: Decimal | None = None
    net_wealth_previous_year: Decimal | None = None
    lifestyle_expenses: Decimal | None = None
    other_outflow_losses: Decimal | None = None
    business_assets: Decimal | None = None
    non_agricultural_property: Decimal | None = None
    agricultural_property: Decimal | None = None
    financial_assets_dps: Decimal | None = None
    financial_assets_others: Decimal | None = None
    motor_vehicles_value: Decimal | None = None
    ornaments_gold_value: Decimal | None = None
    furniture_electronics_value: Decimal | None = None
    cash_in_hand: Decimal | None = None
    bank_balances: Decimal | None = None
    other_deposits: Decimal | None = None
    institutional_liabilities: Decimal | None = None
    non_institutional_liabilities: Decimal | None = None


class IT10BReconciliationDetails(BaseModel):
    total_fund_inflow: Decimal
    gross_wealth: Decimal
    total_liabilities: Decimal
    net_wealth_closing: Decimal
    change_in_net_wealth: Decimal
    total_fund_outflow: Decimal
    difference: Decimal
    is_balanced: bool


class IT10BStatementResponse(IT10BStatementBase):
    id: uuid.UUID
    user_id: uuid.UUID
    financial_year: str
    assessment_year: str
    lifestyle_expenses: Decimal
    total_fund_inflow: Decimal
    total_fund_outflow: Decimal
    gross_wealth: Decimal
    total_liabilities: Decimal
    net_wealth_closing: Decimal
    change_in_net_wealth: Decimal
    difference: Decimal
    is_balanced: bool
    asset_items: list[IT10BAssetItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IT10BAutoBalanceResponse(BaseModel):
    statement_id: uuid.UUID
    previous_cash_in_hand: Decimal
    adjusted_cash_in_hand: Decimal
    difference_reconciled: Decimal
    is_balanced: bool

