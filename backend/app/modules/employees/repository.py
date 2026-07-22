import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.employees.model import Employee
from app.modules.employees.schema import EmployeeCreate, EmployeeUpdate
from app.modules.users.model import User
from app.modules.employers.model import Employer


class EmployeeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, employee_id: uuid.UUID) -> Employee | None:
        """Fetch employee by primary key ID."""
        statement = select(Employee).where(Employee.id == employee_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Employee | None:
        """Fetch employee by linked user ID."""
        statement = select(Employee).where(Employee.user_id == user_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_nid(self, nid: str) -> Employee | None:
        """Fetch employee by NID."""
        statement = select(Employee).where(Employee.nid == nid)
        result = await self.db.exec(statement)
        return result.first()

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[Employee]:
        """Fetch all employees with pagination."""
        statement = select(Employee).offset(offset).limit(limit)
        result = await self.db.exec(statement)
        return list(result.all())

    async def get_detailed(self, employee_id: uuid.UUID) -> tuple[Employee, User, Employer | None] | None:
        """Get employee combined with its User and Employer details."""
        statement = (
            select(Employee, User, Employer)
            .join(User, Employee.user_id == User.id)
            .outerjoin(Employer, Employee.employer_id == Employer.id)
            .where(Employee.id == employee_id)
        )
        result = await self.db.exec(statement)
        row = result.first()
        if not row:
            return None
        return row  # Returns (Employee, User, Employer or None)

    async def get_detailed_by_user_id(self, user_id: uuid.UUID) -> tuple[Employee, User, Employer | None] | None:
        """Get employee combined with User and Employer details by User ID."""
        statement = (
            select(Employee, User, Employer)
            .join(User, Employee.user_id == User.id)
            .outerjoin(Employer, Employee.employer_id == Employer.id)
            .where(Employee.user_id == user_id)
        )
        result = await self.db.exec(statement)
        row = result.first()
        if not row:
            return None
        return row

    async def get_all_detailed(self, offset: int = 0, limit: int = 100) -> list[tuple[Employee, User, Employer | None]]:
        """Get all employee profiles with nested user and company info."""
        statement = (
            select(Employee, User, Employer)
            .join(User, Employee.user_id == User.id)
            .outerjoin(Employer, Employee.employer_id == Employer.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.exec(statement)
        return list(result.all())

    async def create(self, user_id: uuid.UUID, employee_create: EmployeeCreate) -> Employee:
        """Create and persist an employee profile linked to a user."""
        db_employee = Employee(
            user_id=user_id,
            employer_id=employee_create.employer_id,
            designation=employee_create.designation,
            department=employee_create.department,
            date_of_joining=employee_create.date_of_joining,
            nid=employee_create.nid,
            tax_zone=employee_create.tax_zone,
            tax_circle=employee_create.tax_circle,
            gender=employee_create.gender,
            is_disabled=employee_create.is_disabled,
            is_freedom_fighter=employee_create.is_freedom_fighter,
            location=employee_create.location
        )
        self.db.add(db_employee)
        await self.db.flush()
        return db_employee

    async def update(self, db_employee: Employee, employee_update: EmployeeUpdate) -> Employee:
        """Update employee profile attributes."""
        update_data = employee_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_employee, key, value)
        
        self.db.add(db_employee)
        await self.db.flush()
        return db_employee

    async def delete(self, db_employee: Employee) -> None:
        """Delete employee profile."""
        await self.db.delete(db_employee)
        await self.db.flush()
