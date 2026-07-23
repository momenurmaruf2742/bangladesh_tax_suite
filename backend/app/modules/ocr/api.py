from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.modules.auth.dependencies import get_current_user
from app.modules.users.schema import UserResponse
from app.modules.ocr.service import OcrService

router = APIRouter(tags=["OCR Document Parser"])


@router.post("/parse-salary-pdf")
async def parse_salary_pdf(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Extract salary components & AIT tax figures automatically from uploaded Salary Slip/Certificate PDF."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported for OCR parsing."
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    result = OcrService.parse_salary_pdf(content)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result["message"]
        )

    return result
