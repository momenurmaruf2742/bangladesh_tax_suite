from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.salaries.schema import (
    SalarySlipCreate,
    SalarySlipResponse,
    SalarySlipSummaryResponse,
    SalaryCertificateResponse
)
from app.modules.salaries.service import SalaryService

router = APIRouter(tags=["Salaries"])


# Salary Slip Endpoints
@router.post("/slips", response_model=SalarySlipResponse, status_code=status.HTTP_201_CREATED)
async def add_or_update_salary_slip(
    slip_in: SalarySlipCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new monthly salary slip or update an existing one if the month matches."""
    service = SalaryService(db)
    return await service.create_or_update_slip(current_user.id, slip_in)


@router.get("/slips", response_model=list[SalarySlipResponse])
async def list_my_salary_slips(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all monthly salary slips for the logged in user's profile."""
    service = SalaryService(db)
    return await service.get_my_slips(current_user.id)


@router.post("/upload-slip-pdf", response_model=SalarySlipResponse, status_code=status.HTTP_201_CREATED)
async def upload_monthly_payslip_pdf(
    file: UploadFile = File(..., description="Monthly Payslip PDF document"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a monthly payslip PDF document and auto-extract month, gross, TDS, and allowances."""
    service = SalaryService(db)
    file_content = await file.read()
    return await service.parse_and_save_monthly_payslip(
        user_id=current_user.id,
        file_content=file_content,
        file_name=file.filename
    )



@router.get("/summary", response_model=SalarySlipSummaryResponse)
async def get_salary_summary(
    financial_year: str = "2025-2026",
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the sum of all monthly salary slips matching a specific financial year."""
    service = SalaryService(db)
    return await service.get_summary_for_year(current_user.id, financial_year)


# Salary Certificate Endpoints
@router.post("/upload-certificate", response_model=SalaryCertificateResponse, status_code=status.HTTP_201_CREATED)
async def upload_salary_certificate(
    financial_year: str = Form(..., description="Financial year, e.g. 2025-2026"),
    file: UploadFile = File(..., description="Annual Salary Certificate PDF issued by HR"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a salary certificate PDF document and auto-extract component totals."""
    service = SalaryService(db)
    file_content = await file.read()
    return await service.save_salary_certificate(
        user_id=current_user.id,
        financial_year=financial_year,
        file_content=file_content,
        file_name=file.filename
    )


@router.get("/certificates", response_model=list[SalaryCertificateResponse])
async def list_my_salary_certificates(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all uploaded annual salary certificates."""
    service = SalaryService(db)
    return await service.get_my_certificates(current_user.id)


@router.put("/certificates/{cert_id}", response_model=SalaryCertificateResponse)
async def update_certificate_totals(
    cert_id: uuid.UUID,
    updates: dict,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually edit or correct the extracted values on a salary certificate."""
    service = SalaryService(db)
    return await service.update_certificate_values(current_user.id, cert_id, updates)


@router.delete("/certificates/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salary_certificate(
    cert_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an uploaded salary certificate and its corresponding file."""
    service = SalaryService(db)
    await service.delete_certificate(current_user.id, cert_id)
    return None


@router.delete("/slips/{slip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salary_slip(
    slip_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a monthly salary slip log."""
    service = SalaryService(db)
    await service.delete_salary_slip(current_user.id, slip_id)
    return None
