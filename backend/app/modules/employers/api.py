from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user, get_current_active_ca_or_admin, get_current_active_admin
from app.modules.employers.schema import EmployerCreate, EmployerUpdate, EmployerResponse
from app.modules.employers.service import EmployerService

router = APIRouter(tags=["Employers"])


@router.post("/", response_model=EmployerResponse, status_code=status.HTTP_201_CREATED)
async def create_employer(
    employer_in: EmployerCreate,
    current_user=Depends(get_current_active_ca_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new employer company profile. (Admin/CA only)"""
    service = EmployerService(db)
    return await service.create_employer(employer_in)


@router.get("/", response_model=list[EmployerResponse])
async def list_employers(
    offset: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all registered employers. (Any authenticated user)"""
    service = EmployerService(db)
    return await service.get_all(offset, limit)


@router.get("/{employer_id}", response_model=EmployerResponse)
async def get_employer(
    employer_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information of a specific employer by ID. (Any authenticated user)"""
    service = EmployerService(db)
    return await service.get_employer_by_id(employer_id)


@router.put("/{employer_id}", response_model=EmployerResponse)
async def update_employer(
    employer_id: uuid.UUID,
    employer_in: EmployerUpdate,
    current_user=Depends(get_current_active_ca_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update details of an employer. (Admin/CA only)"""
    service = EmployerService(db)
    return await service.update_employer(employer_id, employer_in)


@router.delete("/{employer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employer(
    employer_id: uuid.UUID,
    current_user=Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete an employer profile. (Admin only)"""
    service = EmployerService(db)
    await service.delete_employer(employer_id)
    return None
