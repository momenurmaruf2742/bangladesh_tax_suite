from fastapi import APIRouter, Depends, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.investments.schema import (
    InvestmentCreate,
    InvestmentUpdate,
    InvestmentResponse,
    AITRecordCreate,
    AITRecordUpdate,
    AITRecordResponse,
    RebateSummaryResponse
)
from app.modules.investments.service import InvestmentService

router = APIRouter(tags=["Investments & AIT"])


# Investment Routes
@router.post("/investments", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
async def add_investment(
    invest_in: InvestmentCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new tax-rebate-eligible investment."""
    service = InvestmentService(db)
    return await service.create_investment(current_user.id, invest_in)


@router.get("/investments", response_model=list[InvestmentResponse])
async def list_investments(
    financial_year: str | None = Query(None, description="Filter by year, e.g. 2025-2026"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all registered investments for the user."""
    service = InvestmentService(db)
    return await service.get_investments(current_user.id, financial_year)


@router.put("/investments/{invest_id}", response_model=InvestmentResponse)
async def update_investment_record(
    invest_id: uuid.UUID,
    invest_in: InvestmentUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Modify details of an existing investment record."""
    service = InvestmentService(db)
    return await service.update_investment(current_user.id, invest_id, invest_in)


@router.delete("/investments/{invest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment_record(
    invest_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an investment record."""
    service = InvestmentService(db)
    await service.delete_investment(current_user.id, invest_id)
    return None


# AIT Routes
@router.post("/ait", response_model=AITRecordResponse, status_code=status.HTTP_201_CREATED)
async def add_ait_record(
    ait_in: AITRecordCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add an Advance Income Tax (AIT) source deduction record."""
    service = InvestmentService(db)
    return await service.create_ait(current_user.id, ait_in)


@router.get("/ait", response_model=list[AITRecordResponse])
async def list_ait_records(
    financial_year: str | None = Query(None, description="Filter by year, e.g. 2025-2026"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all registered AIT records for the user."""
    service = InvestmentService(db)
    return await service.get_aits(current_user.id, financial_year)


@router.put("/ait/{ait_id}", response_model=AITRecordResponse)
async def update_ait_record(
    ait_id: uuid.UUID,
    ait_in: AITRecordUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Modify details of an existing AIT record."""
    service = InvestmentService(db)
    return await service.update_ait(current_user.id, ait_id, ait_in)


@router.delete("/ait/{ait_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ait_record(
    ait_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an AIT record."""
    service = InvestmentService(db)
    await service.delete_ait(current_user.id, ait_id)
    return None


# Summary Route
@router.get("/summary", response_model=RebateSummaryResponse)
async def get_rebate_summary(
    financial_year: str = "2025-2026",
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get summarized investment and AIT aggregates for tax calculations."""
    service = InvestmentService(db)
    return await service.get_rebate_summary(current_user.id, financial_year)
