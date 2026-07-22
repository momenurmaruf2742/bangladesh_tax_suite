import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.investments.model import Investment, AITRecord
from app.modules.investments.schema import (
    InvestmentCreate,
    InvestmentUpdate,
    AITRecordCreate,
    AITRecordUpdate
)


class InvestmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Investment Methods
    async def get_investment_by_id(self, invest_id: uuid.UUID) -> Investment | None:
        statement = select(Investment).where(Investment.id == invest_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_investments_by_employee(self, employee_id: uuid.UUID) -> list[Investment]:
        statement = select(Investment).where(Investment.employee_id == employee_id)
        result = await self.db.exec(statement)
        return list(result.all())

    async def get_investments_by_year(self, employee_id: uuid.UUID, financial_year: str) -> list[Investment]:
        statement = select(Investment).where(
            (Investment.employee_id == employee_id) & (Investment.financial_year == financial_year)
        )
        result = await self.db.exec(statement)
        return list(result.all())

    async def create_investment(self, employee_id: uuid.UUID, invest_create: InvestmentCreate) -> Investment:
        db_invest = Investment(
            employee_id=employee_id,
            financial_year=invest_create.financial_year,
            category=invest_create.category,
            amount=invest_create.amount,
            description=invest_create.description
        )
        self.db.add(db_invest)
        await self.db.flush()
        return db_invest

    async def update_investment(self, db_invest: Investment, invest_update: InvestmentUpdate) -> Investment:
        update_data = invest_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_invest, key, value)
        self.db.add(db_invest)
        await self.db.flush()
        return db_invest

    async def delete_investment(self, db_invest: Investment) -> None:
        await self.db.delete(db_invest)
        await self.db.flush()

    # AIT Methods
    async def get_ait_by_id(self, ait_id: uuid.UUID) -> AITRecord | None:
        statement = select(AITRecord).where(AITRecord.id == ait_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_aits_by_employee(self, employee_id: uuid.UUID) -> list[AITRecord]:
        statement = select(AITRecord).where(AITRecord.employee_id == employee_id)
        result = await self.db.exec(statement)
        return list(result.all())

    async def get_aits_by_year(self, employee_id: uuid.UUID, financial_year: str) -> list[AITRecord]:
        statement = select(AITRecord).where(
            (AITRecord.employee_id == employee_id) & (AITRecord.financial_year == financial_year)
        )
        result = await self.db.exec(statement)
        return list(result.all())

    async def create_ait(self, employee_id: uuid.UUID, ait_create: AITRecordCreate) -> AITRecord:
        db_ait = AITRecord(
            employee_id=employee_id,
            financial_year=ait_create.financial_year,
            category=ait_create.category,
            amount=ait_create.amount,
            challan_number=ait_create.challan_number,
            challan_date=ait_create.challan_date,
            description=ait_create.description
        )
        self.db.add(db_ait)
        await self.db.flush()
        return db_ait

    async def update_ait(self, db_ait: AITRecord, ait_update: AITRecordUpdate) -> AITRecord:
        update_data = ait_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ait, key, value)
        self.db.add(db_ait)
        await self.db.flush()
        return db_ait

    async def delete_ait(self, db_ait: AITRecord) -> None:
        await self.db.delete(db_ait)
        await self.db.flush()
