from datetime import datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field, ConfigDict


class SalarySlipBase(BaseModel):
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM format")
    basic_salary: Decimal = Field(default=Decimal("0.0"), ge=0)
    house_rent: Decimal = Field(default=Decimal("0.0"), ge=0)
    medical_allowance: Decimal = Field(default=Decimal("0.0"), ge=0)
    conveyance: Decimal = Field(default=Decimal("0.0"), ge=0)
    festival_bonus: Decimal = Field(default=Decimal("0.0"), ge=0)
    provident_fund: Decimal = Field(default=Decimal("0.0"), ge=0, description="Employee RPF portion")
    employer_provident_fund: Decimal = Field(default=Decimal("0.0"), ge=0, description="Employer RPF portion")
    other_allowances: Decimal = Field(default=Decimal("0.0"), ge=0)
    tax_deducted: Decimal = Field(default=Decimal("0.0"), ge=0, description="Monthly TDS")
    doc_path: str | None = Field(default=None, description="Path to uploaded monthly payslip PDF")


class SalarySlipCreate(SalarySlipBase):
    pass


class SalarySlipUpdate(BaseModel):
    basic_salary: Decimal | None = None
    house_rent: Decimal | None = None
    medical_allowance: Decimal | None = None
    conveyance: Decimal | None = None
    festival_bonus: Decimal | None = None
    provident_fund: Decimal | None = None
    employer_provident_fund: Decimal | None = None
    other_allowances: Decimal | None = None
    tax_deducted: Decimal | None = None
    doc_path: str | None = None


class SalarySlipResponse(SalarySlipBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class SalarySlipSummaryResponse(BaseModel):
    financial_year: str
    months_count: int
    total_basic: Decimal
    total_house_rent: Decimal
    total_medical: Decimal
    total_conveyance: Decimal
    total_bonus: Decimal
    total_provident_fund: Decimal
    total_employer_provident_fund: Decimal
    total_other_allowances: Decimal
    total_tax_deducted: Decimal
    gross_salary: Decimal
    total_taxable_salary: Decimal | None = None  # To be calculated in tax engine later


class SalaryCertificateResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    financial_year: str
    file_name: str
    status: str
    total_basic: Decimal
    total_house_rent: Decimal
    total_medical: Decimal
    total_conveyance: Decimal
    total_bonus: Decimal
    total_provident_fund: Decimal
    total_tax_deducted: Decimal
    total_others: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
