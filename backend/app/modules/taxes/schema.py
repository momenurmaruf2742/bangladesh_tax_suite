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
