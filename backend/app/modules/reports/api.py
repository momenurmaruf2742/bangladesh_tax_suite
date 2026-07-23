from fastapi import APIRouter, Depends, Query, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.schema import UserResponse
from app.modules.reports.service import ReportService

router = APIRouter(tags=["Reports & Exports"])


@router.get("/tax-return/pdf")
async def download_tax_return_pdf(
    financial_year: str = Query("2025-2026", description="Financial Year, e.g. 2025-2026"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download official PDF Tax Return & Computation Sheet."""
    report_service = ReportService(db)
    pdf_bytes = await report_service.generate_tax_return_pdf(current_user.id, financial_year)
    
    filename = f"Tax_Return_Summary_{financial_year}_{current_user.first_name}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/salary/excel")
async def download_salary_excel(
    financial_year: str = Query("2025-2026", description="Financial Year, e.g. 2025-2026"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download Excel spreadsheet of Salary Slips and Investments."""
    report_service = ReportService(db)
    excel_bytes = await report_service.generate_salary_excel(current_user.id, financial_year)
    
    filename = f"Salary_Log_{financial_year}_{current_user.first_name}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
