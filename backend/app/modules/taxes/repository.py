import uuid

from app.modules.taxes.model import (
    IT10BAssetItem,
    IT10BStatement,
    LifestyleExpense,
    TaxCalculation,
    TaxRule,
)
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


class IT10BRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, statement_id: uuid.UUID) -> IT10BStatement | None:
        """Fetch IT-10B statement by ID."""
        statement = select(IT10BStatement).where(IT10BStatement.id == statement_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_user_and_year(
        self, user_id: uuid.UUID, financial_year: str
    ) -> IT10BStatement | None:
        """Fetch IT-10B statement for a user and financial year."""
        statement = (
            select(IT10BStatement)
            .where(IT10BStatement.user_id == user_id)
            .where(IT10BStatement.financial_year == financial_year)
            .order_by(IT10BStatement.created_at.desc())
        )
        result = await self.db.exec(statement)
        return result.first()

    async def get_history_by_user(
        self, user_id: uuid.UUID
    ) -> list[IT10BStatement]:
        """Fetch all historical IT-10B statements for a user."""
        statement = (
            select(IT10BStatement)
            .where(IT10BStatement.user_id == user_id)
            .order_by(IT10BStatement.financial_year.desc())
        )
        result = await self.db.exec(statement)
        return list(result.all())

    async def create(self, statement_obj: IT10BStatement) -> IT10BStatement:
        """Save a new IT-10B statement."""
        self.db.add(statement_obj)
        await self.db.flush()
        return statement_obj

    async def delete(self, statement_obj: IT10BStatement) -> None:
        """Delete an IT-10B statement."""
        await self.db.delete(statement_obj)
        await self.db.flush()


class IT10BAssetItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, item_id: uuid.UUID) -> IT10BAssetItem | None:
        """Fetch asset item by ID."""
        statement = select(IT10BAssetItem).where(IT10BAssetItem.id == item_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_statement(
        self, statement_id: uuid.UUID
    ) -> list[IT10BAssetItem]:
        """Fetch all asset items belonging to an IT-10B statement."""
        statement = (
            select(IT10BAssetItem)
            .where(IT10BAssetItem.statement_id == statement_id)
            .order_by(IT10BAssetItem.created_at.asc())
        )
        result = await self.db.exec(statement)
        return list(result.all())

    async def create(self, item: IT10BAssetItem) -> IT10BAssetItem:
        """Add a detailed asset item."""
        self.db.add(item)
        await self.db.flush()
        return item

    async def delete(self, item: IT10BAssetItem) -> None:
        """Delete an asset item."""
        await self.db.delete(item)
        await self.db.flush()


class LifestyleExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, expense_id: uuid.UUID) -> LifestyleExpense | None:
        """Fetch lifestyle expense record by ID."""
        statement = select(LifestyleExpense).where(LifestyleExpense.id == expense_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_user_and_year(
        self, user_id: uuid.UUID, financial_year: str
    ) -> LifestyleExpense | None:
        """Fetch lifestyle expense for a user and financial year."""
        statement = (
            select(LifestyleExpense)
            .where(LifestyleExpense.user_id == user_id)
            .where(LifestyleExpense.financial_year == financial_year)
            .order_by(LifestyleExpense.created_at.desc())
        )
        result = await self.db.exec(statement)
        return result.first()

    async def get_history_by_user(
        self, user_id: uuid.UUID
    ) -> list[LifestyleExpense]:
        """Fetch all historical lifestyle expenses for a user."""
        statement = (
            select(LifestyleExpense)
            .where(LifestyleExpense.user_id == user_id)
            .order_by(LifestyleExpense.financial_year.desc())
        )
        result = await self.db.exec(statement)
        return list(result.all())

    async def create(self, expense: LifestyleExpense) -> LifestyleExpense:
        """Save a new lifestyle expense record."""
        self.db.add(expense)
        await self.db.flush()
        return expense

    async def delete(self, expense: LifestyleExpense) -> None:
        """Delete a lifestyle expense record."""
        await self.db.delete(expense)
        await self.db.flush()

