import uuid

from app.db.database import get_db
from app.modules.auth.dependencies import get_current_active_admin, get_current_user
from app.modules.taxes.model import TaxRule
from app.modules.taxes.repository import TaxRuleRepository
from app.modules.taxes.schema import (
    TaxCalculationCreate,
    TaxCalculationResponse,
    TaxDetailsResponse,
    TaxRuleCreate,
    TaxRuleResponse,
    TaxRuleUpdate,
)
from app.modules.taxes.service import TaxService
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(tags=["Taxes"])


@router.post("/calculate", response_model=TaxDetailsResponse)
async def calculate_tax_details(
    payload: TaxCalculationCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate tax details dynamically without saving."""
    service = TaxService(db)
    return await service.calculate_tax(
        user_id=current_user.id,
        financial_year=payload.financial_year,
        other_income=payload.other_income,
    )


@router.post("/calculate-save", response_model=TaxDetailsResponse)
async def calculate_and_save_tax_details(
    payload: TaxCalculationCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate tax details and save/overwrite in database."""
    service = TaxService(db)
    return await service.calculate_and_save_tax(
        user_id=current_user.id,
        financial_year=payload.financial_year,
        other_income=payload.other_income,
    )


@router.get("/history", response_model=list[TaxCalculationResponse])
async def get_calculation_history(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieve saved historical calculations for the logged-in user."""
    service = TaxService(db)
    return await service.get_calculation_history(current_user.id)


@router.delete("/history/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calculation_run(
    calc_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved historical tax calculation record."""
    service = TaxService(db)
    await service.delete_calculation_run(current_user.id, calc_id)
    return None


@router.get("/history/{calc_id}/return/html", response_class=HTMLResponse)
async def get_tax_return_html(
    calc_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a printable NBR IT-1152023 Individual Income Tax Return form in HTML format."""
    service = TaxService(db)
    details = await service.get_calculation_details(current_user.id, calc_id)
    html_content = service.generate_return_html(details)
    return HTMLResponse(content=html_content)


# --- Dynamic Rules Engine Endpoints (Admin Controlled) ---


@router.get("/rules", response_model=list[TaxRuleResponse])
async def get_all_tax_rules(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieve all configured tax rules."""
    repo = TaxRuleRepository(db)
    rules = await repo.get_all()
    if not rules:
        service = TaxService(db)
        from app.core.tax_rules import TAX_YEAR_RULES

        for year in TAX_YEAR_RULES.keys():
            await service._get_applicable_rules(year)
        rules = await repo.get_all()
    return rules


@router.get("/rules/{financial_year}", response_model=TaxRuleResponse)
async def get_tax_rule_by_year(
    financial_year: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve rules for a specific financial year."""
    repo = TaxRuleRepository(db)
    rule = await repo.get_by_year(financial_year)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tax rules for financial year '{financial_year}' not found.",
        )
    return rule


@router.post(
    "/rules", response_model=TaxRuleResponse, status_code=status.HTTP_201_CREATED
)
async def create_tax_rule(
    payload: TaxRuleCreate,
    current_admin=Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create new tax rules for a financial year (Admin only)."""
    repo = TaxRuleRepository(db)
    existing = await repo.get_by_year(payload.financial_year)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rules for financial year '{payload.financial_year}' already configured. Use PUT to update.",
        )

    rule = TaxRule(**payload.model_dump())
    return await repo.create(rule)


@router.put("/rules/{financial_year}", response_model=TaxRuleResponse)
async def update_tax_rule(
    financial_year: str,
    payload: TaxRuleUpdate,
    current_admin=Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update tax rules for a financial year (Admin only)."""
    repo = TaxRuleRepository(db)
    rule = await repo.get_by_year(financial_year)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rules for '{financial_year}' not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(rule, key, val)

    db.add(rule)
    await db.flush()
    return rule


@router.delete("/rules/{financial_year}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tax_rule(
    financial_year: str,
    current_admin=Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete configured tax rules for a financial year (Admin only)."""
    repo = TaxRuleRepository(db)
    rule = await repo.get_by_year(financial_year)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rules for '{financial_year}' not found.",
        )

    await repo.delete(rule)
    return None
