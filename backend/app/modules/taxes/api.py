import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.taxes.schema import TaxCalculationCreate, TaxDetailsResponse, TaxCalculationResponse
from app.modules.taxes.service import TaxService

router = APIRouter(tags=["Taxes"])


@router.post("/calculate", response_model=TaxDetailsResponse)
async def calculate_tax_details(
    payload: TaxCalculationCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate tax details dynamically without saving."""
    service = TaxService(db)
    return await service.calculate_tax(
        user_id=current_user.id,
        financial_year=payload.financial_year,
        other_income=payload.other_income
    )


@router.post("/calculate-save", response_model=TaxDetailsResponse)
async def calculate_and_save_tax_details(
    payload: TaxCalculationCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate tax details and save/overwrite in database."""
    service = TaxService(db)
    return await service.calculate_and_save_tax(
        user_id=current_user.id,
        financial_year=payload.financial_year,
        other_income=payload.other_income
    )


@router.get("/history", response_model=list[TaxCalculationResponse])
async def get_calculation_history(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve saved historical calculations for the logged-in user."""
    service = TaxService(db)
    return await service.get_calculation_history(current_user.id)


@router.delete("/history/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calculation_run(
    calc_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a saved historical tax calculation record."""
    service = TaxService(db)
    await service.delete_calculation_run(current_user.id, calc_id)
    return None


@router.get("/history/{calc_id}/return/html", response_class=HTMLResponse)
async def get_tax_return_html(
    calc_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a printable NBR IT-1152023 Individual Income Tax Return form in HTML format."""
    service = TaxService(db)
    details = await service.get_calculation_details(current_user.id, calc_id)
    html_content = service.generate_return_html(details)
    return HTMLResponse(content=html_content)
