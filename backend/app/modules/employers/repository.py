import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.employers.model import Employer
from app.modules.employers.schema import EmployerCreate, EmployerUpdate


class EmployerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, employer_id: uuid.UUID) -> Employer | None:
        """Fetch employer by primary key ID."""
        statement = select(Employer).where(Employer.id == employer_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_bin(self, bin_str: str) -> Employer | None:
        """Fetch employer by unique BIN."""
        statement = select(Employer).where(Employer.bin == bin_str)
        result = await self.db.exec(statement)
        return result.first()

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[Employer]:
        """Fetch all employers with offset/limit pagination."""
        statement = select(Employer).offset(offset).limit(limit)
        result = await self.db.exec(statement)
        return list(result.all())

    async def create(self, employer_create: EmployerCreate) -> Employer:
        """Create and persist a new employer."""
        db_employer = Employer(
            name=employer_create.name,
            address=employer_create.address,
            bin=employer_create.bin,
            contact_email=employer_create.contact_email,
            contact_phone=employer_create.contact_phone
        )
        self.db.add(db_employer)
        await self.db.flush()
        return db_employer

    async def update(self, db_employer: Employer, employer_update: EmployerUpdate) -> Employer:
        """Update an existing employer's attributes."""
        update_data = employer_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_employer, key, value)
        
        self.db.add(db_employer)
        await self.db.flush()
        return db_employer

    async def delete(self, db_employer: Employer) -> None:
        """Delete an employer."""
        await self.db.delete(db_employer)
        await self.db.flush()
