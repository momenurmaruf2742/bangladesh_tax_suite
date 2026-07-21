from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user, get_current_active_ca_or_admin, get_current_active_admin
from app.modules.employees.schema import EmployeeCreate, EmployeeUpdate, EmployeeDetailedResponse
from app.modules.employees.service import EmployeeService

router = APIRouter(tags=["Employees"])


@router.post("/profile", response_model=EmployeeDetailedResponse)
async def setup_my_profile(
    employee_in: EmployeeCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update the logged-in user's own employee profile."""
    service = EmployeeService(db)
    return await service.create_or_update_my_profile(current_user.id, employee_in)


@router.get("/profile", response_model=EmployeeDetailedResponse)
async def get_my_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the logged-in user's own detailed employee profile."""
    service = EmployeeService(db)
    return await service.get_profile_by_user_id(current_user.id)


@router.get("/", response_model=list[EmployeeDetailedResponse])
async def list_employees(
    offset: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_active_ca_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all registered employee profiles. (Admin/CA only)"""
    service = EmployeeService(db)
    return await service.get_all(offset, limit)


@router.get("/{employee_id}", response_model=EmployeeDetailedResponse)
async def get_employee(
    employee_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific employee profile. (Admin/CA, or the employee owner)"""
    service = EmployeeService(db)
    profile = await service.get_by_id(employee_id)
    
    # Check permissions: must be Admin, CA, or the owner of the profile
    if current_user.role not in ["Admin", "CA"] and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this employee profile"
        )
        
    return profile


@router.put("/{employee_id}", response_model=EmployeeDetailedResponse)
async def update_employee(
    employee_id: uuid.UUID,
    employee_in: EmployeeUpdate,
    current_user=Depends(get_current_active_ca_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update an employee profile by ID. (Admin/CA only)"""
    service = EmployeeService(db)
    return await service.update_employee_profile(employee_id, employee_in)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: uuid.UUID,
    current_user=Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete an employee profile. (Admin only)"""
    service = EmployeeService(db)
    await service.delete_employee(employee_id)
    return None
