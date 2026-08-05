import uuid

from app.modules.taxes.model import TaxCalculation, TaxRule
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class TaxRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, calc_id: uuid.UUID) -> TaxCalculation | None:
        """Fetch tax calculation by ID."""
        statement = select(TaxCalculation).where(TaxCalculation.id == calc_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_employee_and_year(
        self, employee_id: uuid.UUID, financial_year: str
    ) -> TaxCalculation | None:
        """Fetch tax calculation for employee and financial year."""
        statement = (
            select(TaxCalculation)
            .where(TaxCalculation.employee_id == employee_id)
            .where(TaxCalculation.financial_year == financial_year)
            .order_by(TaxCalculation.created_at.desc())
        )
        result = await self.db.exec(statement)
        return result.first()

    async def get_history_by_employee(
        self, employee_id: uuid.UUID
    ) -> list[TaxCalculation]:
        """Fetch all historical calculations for an employee."""
        statement = (
            select(TaxCalculation)
            .where(TaxCalculation.employee_id == employee_id)
            .order_by(TaxCalculation.created_at.desc())
        )
        result = await self.db.exec(statement)
        return list(result.all())

    async def create(
        self, employee_id: uuid.UUID, calc: TaxCalculation
    ) -> TaxCalculation:
        """Save a new tax calculation."""
        calc.employee_id = employee_id
        self.db.add(calc)
        await self.db.flush()
        return calc

    async def delete(self, calc: TaxCalculation) -> None:
        """Remove a saved tax calculation."""
        await self.db.delete(calc)
        await self.db.flush()


class TaxRuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_year(self, financial_year: str) -> TaxRule | None:
        """Fetch tax rule for specific financial year."""
        statement = select(TaxRule).where(TaxRule.financial_year == financial_year)
        result = await self.db.exec(statement)
        return result.first()

    async def get_all(self) -> list[TaxRule]:
        """Fetch all configured tax rules."""
        statement = select(TaxRule).order_by(TaxRule.financial_year.desc())
        result = await self.db.exec(statement)
        return list(result.all())

    async def create(self, rule: TaxRule) -> TaxRule:
        """Save a new tax rule."""
        self.db.add(rule)
        await self.db.flush()
        return rule

    async def delete(self, rule: TaxRule) -> None:
        """Delete a tax rule."""
        await self.db.delete(rule)
        await self.db.flush()
