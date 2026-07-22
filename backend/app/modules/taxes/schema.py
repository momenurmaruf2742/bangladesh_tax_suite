from datetime import datetime
from decimal import Decimal
import uuid
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
