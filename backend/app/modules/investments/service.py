import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.employees.repository import EmployeeRepository
from app.modules.investments.model import Investment, AITRecord
from app.modules.investments.repository import InvestmentRepository
from app.modules.investments.schema import (
    InvestmentCreate,
    InvestmentUpdate,
    AITRecordCreate,
    AITRecordUpdate,
    RebateSummaryResponse
)


class InvestmentService:
    def __init__(self, db: AsyncSession):
        self.repo = InvestmentRepository(db)
        self.employee_repo = EmployeeRepository(db)

    async def _get_employee_id(self, user_id: uuid.UUID) -> uuid.UUID:
        employee = await self.employee_repo.get_by_user_id(user_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee profile not setup. Please configure employee details first."
            )
        return employee.id

    async def _get_employee_id_or_none(self, user_id: uuid.UUID) -> uuid.UUID | None:
        employee = await self.employee_repo.get_by_user_id(user_id)
        return employee.id if employee else None

    # Investment Actions
    async def create_investment(self, user_id: uuid.UUID, invest_in: InvestmentCreate) -> Investment:
        employee_id = await self._get_employee_id(user_id)
        return await self.repo.create_investment(employee_id, invest_in)

    async def update_investment(
        self,
        user_id: uuid.UUID,
        invest_id: uuid.UUID,
        invest_in: InvestmentUpdate
    ) -> Investment:
        employee_id = await self._get_employee_id(user_id)
        db_invest = await self.repo.get_investment_by_id(invest_id)
        if not db_invest or db_invest.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investment record not found"
            )
        return await self.repo.update_investment(db_invest, invest_in)

    async def delete_investment(self, user_id: uuid.UUID, invest_id: uuid.UUID) -> None:
        employee_id = await self._get_employee_id(user_id)
        db_invest = await self.repo.get_investment_by_id(invest_id)
        if not db_invest or db_invest.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investment record not found"
            )
        await self.repo.delete_investment(db_invest)

    async def get_investments(self, user_id: uuid.UUID, financial_year: str | None = None) -> list[Investment]:
        employee_id = await self._get_employee_id_or_none(user_id)
        if not employee_id:
            return []
        if financial_year:
            return await self.repo.get_investments_by_year(employee_id, financial_year)
        return await self.repo.get_investments_by_employee(employee_id)

    # AIT Actions
    async def create_ait(self, user_id: uuid.UUID, ait_in: AITRecordCreate) -> AITRecord:
        employee_id = await self._get_employee_id(user_id)
        return await self.repo.create_ait(employee_id, ait_in)

    async def update_ait(
        self,
        user_id: uuid.UUID,
        ait_id: uuid.UUID,
        ait_in: AITRecordUpdate
    ) -> AITRecord:
        employee_id = await self._get_employee_id(user_id)
        db_ait = await self.repo.get_ait_by_id(ait_id)
        if not db_ait or db_ait.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AIT record not found"
            )
        return await self.repo.update_ait(db_ait, ait_in)

    async def delete_ait(self, user_id: uuid.UUID, ait_id: uuid.UUID) -> None:
        employee_id = await self._get_employee_id(user_id)
        db_ait = await self.repo.get_ait_by_id(ait_id)
        if not db_ait or db_ait.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AIT record not found"
            )
        await self.repo.delete_ait(db_ait)

    async def get_aits(self, user_id: uuid.UUID, financial_year: str | None = None) -> list[AITRecord]:
        employee_id = await self._get_employee_id_or_none(user_id)
        if not employee_id:
            return []
        if financial_year:
            return await self.repo.get_aits_by_year(employee_id, financial_year)
        return await self.repo.get_aits_by_employee(employee_id)

    # Rebate Aggregations
    async def get_rebate_summary(self, user_id: uuid.UUID, financial_year: str) -> RebateSummaryResponse:
        employee_id = await self._get_employee_id_or_none(user_id)
        if not employee_id:
            return RebateSummaryResponse(
                financial_year=financial_year,
                total_invested=Decimal("0.0"),
                total_ait=Decimal("0.0"),
                dps_total=Decimal("0.0"),
                life_insurance_total=Decimal("0.0"),
                sanchayapatra_total=Decimal("0.0"),
                stock_market_total=Decimal("0.0"),
                other_investments_total=Decimal("0.0")
            )
        
        investments = await self.repo.get_investments_by_year(employee_id, financial_year)
        aits = await self.repo.get_aits_by_year(employee_id, financial_year)

        totals = {
            "dps": Decimal("0.0"),
            "life": Decimal("0.0"),
            "sanchaya": Decimal("0.0"),
            "stock": Decimal("0.0"),
            "other": Decimal("0.0"),
        }

        total_invested = Decimal("0.0")
        for inv in investments:
            cat = inv.category.lower()
            amount = inv.amount
            total_invested += amount
            
            if "dps" in cat:
                totals["dps"] += amount
            elif "insurance" in cat or "life" in cat:
                totals["life"] += amount
            elif "sanchaya" in cat or "saving" in cat:
                totals["sanchaya"] += amount
            elif "stock" in cat or "share" in cat or "mutual" in cat:
                totals["stock"] += amount
            else:
                totals["other"] += amount

        total_ait = sum((ait.amount for ait in aits), Decimal("0.0"))

        return RebateSummaryResponse(
            financial_year=financial_year,
            total_invested=total_invested,
            total_ait=total_ait,
            dps_total=totals["dps"],
            life_insurance_total=totals["life"],
            sanchayapatra_total=totals["sanchaya"],
            stock_market_total=totals["stock"],
            other_investments_total=totals["other"]
        )
