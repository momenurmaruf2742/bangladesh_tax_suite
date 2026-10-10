import uuid

from app.db.database import get_db
from app.modules.auth.dependencies import get_current_active_admin, get_current_user
from app.modules.taxes.model import TaxRule
from app.modules.taxes.repository import TaxRuleRepository
from app.modules.taxes.schema import (
    IT10BAssetItemCreate,
    IT10BAssetItemResponse,
    IT10BAutoBalanceResponse,
    IT10BReconciliationDetails,
    IT10BStatementCreate,
    IT10BStatementResponse,
    IT10BStatementUpdate,
    LifestyleExpenseCreate,
    LifestyleExpenseResponse,
    LifestyleExpenseUpdate,
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


# --- IT-10BB Lifestyle Expenses Endpoints ---


@router.get("/it10bb", response_model=LifestyleExpenseResponse)
async def get_lifestyle_expenses(
    financial_year: str = "2025-2026",
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve Lifestyle Expenses (IT-10BB) for current user and financial year with auto-synced TDS."""
    service = TaxService(db)
    return await service.get_or_calculate_lifestyle_expenses(current_user.id, financial_year)


@router.post("/it10bb", response_model=LifestyleExpenseResponse)
async def save_lifestyle_expenses(
    payload: LifestyleExpenseCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save or update Lifestyle Expenses (Form IT-10BB)."""
    service = TaxService(db)
    return await service.save_lifestyle_expenses(current_user.id, payload)


# --- IT-10B Statement of Assets and Liabilities Endpoints ---


@router.get("/it10b", response_model=IT10BStatementResponse)
async def get_it10b_statement(
    financial_year: str = "2025-2026",
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve IT-10B Statement of Assets and Liabilities for current user and financial year."""
    service = TaxService(db)
    statement = await service.calculate_or_get_it10b_statement(current_user.id, financial_year)
    items = []
    if statement.id:
        items = await service.get_statement_asset_items(current_user.id, statement.id)
    resp = IT10BStatementResponse.model_validate(statement)
    resp.asset_items = [IT10BAssetItemResponse.model_validate(it) for it in items]
    return resp


@router.post("/it10b", response_model=IT10BStatementResponse)
async def save_it10b_statement(
    payload: IT10BStatementCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save or update IT-10B Statement of Assets and Liabilities, executing statutory wealth reconciliation."""
    service = TaxService(db)
    statement = await service.save_it10b_statement(current_user.id, payload)
    items = await service.get_statement_asset_items(current_user.id, statement.id)
    resp = IT10BStatementResponse.model_validate(statement)
    resp.asset_items = [IT10BAssetItemResponse.model_validate(it) for it in items]
    return resp


@router.post("/it10b/reconcile", response_model=IT10BReconciliationDetails)
async def preview_it10b_reconciliation(
    payload: IT10BStatementCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Preview IT-10B wealth reconciliation calculation and check if balanced."""
    service = TaxService(db)
    from app.modules.taxes.model import IT10BStatement

    ay = payload.assessment_year or service.derive_assessment_year(payload.financial_year)
    dummy_stmt = IT10BStatement(
        user_id=current_user.id,
        financial_year=payload.financial_year,
        assessment_year=ay,
        **payload.model_dump(
            exclude={"financial_year", "assessment_year", "lifestyle_expenses"}
        ),
    )
    if payload.lifestyle_expenses is not None:
        dummy_stmt.lifestyle_expenses = payload.lifestyle_expenses
    else:
        lifestyle = await service.lifestyle_repo.get_by_user_and_year(
            current_user.id, payload.financial_year
        )
        if lifestyle:
            dummy_stmt.lifestyle_expenses = lifestyle.total_lifestyle_expense

    service.reconcile_wealth(dummy_stmt)
    return IT10BReconciliationDetails(
        total_fund_inflow=dummy_stmt.total_fund_inflow,
        gross_wealth=dummy_stmt.gross_wealth,
        total_liabilities=dummy_stmt.total_liabilities,
        net_wealth_closing=dummy_stmt.net_wealth_closing,
        change_in_net_wealth=dummy_stmt.change_in_net_wealth,
        total_fund_outflow=dummy_stmt.total_fund_outflow,
        difference=dummy_stmt.difference,
        is_balanced=dummy_stmt.is_balanced,
    )


@router.post("/it10b/auto-balance-cash", response_model=IT10BAutoBalanceResponse)
async def auto_balance_cash_in_hand(
    financial_year: str = "2025-2026",
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Auto-adjusts cash_in_hand directly to achieve Difference == 0.00."""
    service = TaxService(db)
    stmt_before = await service.calculate_or_get_it10b_statement(current_user.id, financial_year)
    old_cash = stmt_before.cash_in_hand
    diff = stmt_before.difference
    stmt_after = await service.auto_balance_cash_in_hand(current_user.id, financial_year)
    return IT10BAutoBalanceResponse(
        statement_id=stmt_after.id,
        previous_cash_in_hand=old_cash,
        adjusted_cash_in_hand=stmt_after.cash_in_hand,
        difference_reconciled=diff,
        is_balanced=stmt_after.is_balanced,
    )


@router.post("/it10b/{statement_id}/assets", response_model=IT10BAssetItemResponse)
async def add_it10b_asset_item(
    statement_id: uuid.UUID,
    payload: IT10BAssetItemCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a detailed asset item to IT-10B statement (supports Gift / Inheritance with 0 cost)."""
    service = TaxService(db)
    return await service.add_asset_item(current_user.id, statement_id, payload)


@router.get("/it10b/{statement_id}/assets", response_model=list[IT10BAssetItemResponse])
async def get_it10b_asset_items(
    statement_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed asset items for an IT-10B statement."""
    service = TaxService(db)
    return await service.get_statement_asset_items(current_user.id, statement_id)


@router.delete("/it10b/assets/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_it10b_asset_item(
    item_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an IT-10B detailed asset item."""
    service = TaxService(db)
    await service.delete_asset_item(current_user.id, item_id)
    return None

