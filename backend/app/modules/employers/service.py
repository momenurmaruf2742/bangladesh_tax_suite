import uuid
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.employers.model import Employer
from app.modules.employers.repository import EmployerRepository
from app.modules.employers.schema import EmployerCreate, EmployerUpdate


class EmployerService:
    def __init__(self, db: AsyncSession):
        self.repo = EmployerRepository(db)

    async def create_employer(self, employer_create: EmployerCreate) -> Employer:
        """Create a new employer with uniqueness checks."""
        if employer_create.bin:
            existing = await self.repo.get_by_bin(employer_create.bin)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Employer with BIN {employer_create.bin} already registered"
                )
        return await self.repo.create(employer_create)

    async def get_employer_by_id(self, employer_id: uuid.UUID) -> Employer:
        """Fetch employer or raise 404."""
        employer = await self.repo.get_by_id(employer_id)
        if not employer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employer not found"
            )
        return employer

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[Employer]:
        """Fetch pagination list."""
        return await self.repo.get_all(offset, limit)

    async def update_employer(self, employer_id: uuid.UUID, employer_update: EmployerUpdate) -> Employer:
        """Update existing employer."""
        employer = await self.get_employer_by_id(employer_id)
        
        # Check duplicate BIN if updated
        if employer_update.bin and employer_update.bin != employer.bin:
            existing = await self.repo.get_by_bin(employer_update.bin)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Employer with BIN {employer_update.bin} already registered"
                )
        return await self.repo.update(employer, employer_update)

    async def delete_employer(self, employer_id: uuid.UUID) -> None:
        """Delete existing employer."""
        employer = await self.get_employer_by_id(employer_id)
        await self.repo.delete(employer)
