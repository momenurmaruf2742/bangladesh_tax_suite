from datetime import datetime, date as py_date
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field, ConfigDict


# Investment Schemas
class InvestmentBase(BaseModel):
    financial_year: str = Field(..., description="e.g. 2025-2026")
    category: str = Field(..., description="DPS, Life Insurance, Sanchayapatra, Stock Market, or Other")
    amount: Decimal = Field(..., ge=0)
    description: str | None = None


class InvestmentCreate(InvestmentBase):
    pass


class InvestmentUpdate(BaseModel):
    category: str | None = None
    amount: Decimal | None = None
    description: str | None = None


class InvestmentResponse(InvestmentBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    doc_path: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# AIT Schemas
class AITRecordBase(BaseModel):
    financial_year: str = Field(..., description="e.g. 2025-2026")
    category: str = Field(..., description="Car Registration, Bank Interest TDS, Property Transaction, or Other")
    amount: Decimal = Field(..., ge=0)
    challan_number: str | None = None
    challan_date: py_date | None = None
    description: str | None = None


class AITRecordCreate(AITRecordBase):
    pass


class AITRecordUpdate(BaseModel):
    category: str | None = None
    amount: Decimal | None = None
    challan_number: str | None = None
    challan_date: py_date | None = None
    description: str | None = None


class AITRecordResponse(AITRecordBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    doc_path: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Summary Schemas
class RebateSummaryResponse(BaseModel):
    financial_year: str
    total_invested: Decimal
    total_ait: Decimal
    dps_total: Decimal
    life_insurance_total: Decimal
    sanchayapatra_total: Decimal
    stock_market_total: Decimal
    other_investments_total: Decimal
