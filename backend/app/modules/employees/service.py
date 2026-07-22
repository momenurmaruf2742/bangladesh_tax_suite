import uuid
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.employees.model import Employee
from app.modules.employees.repository import EmployeeRepository
from app.modules.employees.schema import EmployeeCreate, EmployeeUpdate, EmployeeDetailedResponse
from app.modules.users.schema import UserResponse
from app.modules.employers.schema import EmployerResponse
from app.modules.employers.repository import EmployerRepository


class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.repo = EmployeeRepository(db)
        self.employer_repo = EmployerRepository(db)

    def _map_to_detailed(self, employee: Employee, user, employer) -> EmployeeDetailedResponse:
        """Helper to map joined database objects to EmployeeDetailedResponse."""
        return EmployeeDetailedResponse(
            id=employee.id,
            user_id=employee.user_id,
            employer_id=employee.employer_id,
            designation=employee.designation,
            department=employee.department,
            date_of_joining=employee.date_of_joining,
            nid=employee.nid,
            tax_zone=employee.tax_zone,
            tax_circle=employee.tax_circle,
            gender=employee.gender,
            is_disabled=employee.is_disabled,
            is_freedom_fighter=employee.is_freedom_fighter,
            location=employee.location,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
            user=UserResponse.model_validate(user),
            employer=EmployerResponse.model_validate(employer) if employer else None
        )

    async def get_profile_by_user_id(self, user_id: uuid.UUID) -> EmployeeDetailedResponse:
        """Fetch employee profile details for a specific User ID."""
        row = await self.repo.get_detailed_by_user_id(user_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found. Please create one."
            )
        return self._map_to_detailed(row[0], row[1], row[2])

    async def get_by_id(self, employee_id: uuid.UUID) -> EmployeeDetailedResponse:
        """Fetch employee by profile ID."""
        row = await self.repo.get_detailed(employee_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found"
            )
        return self._map_to_detailed(row[0], row[1], row[2])

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[EmployeeDetailedResponse]:
        """Fetch pagination list of all employee profiles."""
        rows = await self.repo.get_all_detailed(offset, limit)
        return [self._map_to_detailed(row[0], row[1], row[2]) for row in rows]

    async def create_or_update_my_profile(self, user_id: uuid.UUID, employee_in: EmployeeCreate) -> EmployeeDetailedResponse:
        """Setup or update the logged-in user's employee details."""
        # 1. Validate employer exists if provided
        if employee_in.employer_id:
            employer = await self.employer_repo.get_by_id(employee_in.employer_id)
            if not employer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified employer company does not exist"
                )

        # 2. Check unique NID
        if employee_in.nid:
            existing_nid = await self.repo.get_by_nid(employee_in.nid)
            if existing_nid and existing_nid.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="NID is already registered to another user"
                )

        # 3. Check if profile already exists
        db_employee = await self.repo.get_by_user_id(user_id)
        if db_employee:
            # Update existing profile
            # Map EmployeeCreate fields to EmployeeUpdate format
            update_data = EmployeeUpdate(**employee_in.model_dump())
            await self.repo.update(db_employee, update_data)
        else:
            # Create new profile
            await self.repo.create(user_id, employee_in)

        # 4. Return detailed response
        return await self.get_profile_by_user_id(user_id)

    async def update_employee_profile(self, employee_id: uuid.UUID, employee_update: EmployeeUpdate) -> EmployeeDetailedResponse:
        """Update any employee's details (typically used by Admin/CA)."""
        row = await self.repo.get_detailed(employee_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found"
            )
        db_employee = row[0]

        # Validate employer if updated
        if employee_update.employer_id:
            employer = await self.employer_repo.get_by_id(employee_update.employer_id)
            if not employer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified employer company does not exist"
                )

        # Check NID uniqueness
        if employee_update.nid and employee_update.nid != db_employee.nid:
            existing_nid = await self.repo.get_by_nid(employee_update.nid)
            if existing_nid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="NID is already registered to another user"
                )

        await self.repo.update(db_employee, employee_update)
        return await self.get_by_id(employee_id)

    async def delete_employee(self, employee_id: uuid.UUID) -> None:
        """Delete employee record (typically Admin only)."""
        row = await self.repo.get_detailed(employee_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found"
            )
        await self.repo.delete(row[0])
