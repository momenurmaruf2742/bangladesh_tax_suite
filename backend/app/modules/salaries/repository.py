import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.salaries.model import SalarySlip, SalaryCertificate
from app.modules.salaries.schema import SalarySlipCreate, SalarySlipUpdate


class SalaryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Monthly Slip Methods
    async def get_slip_by_id(self, slip_id: uuid.UUID) -> SalarySlip | None:
        statement = select(SalarySlip).where(SalarySlip.id == slip_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_slip_by_month(self, employee_id: uuid.UUID, month: str) -> SalarySlip | None:
        statement = select(SalarySlip).where(
            (SalarySlip.employee_id == employee_id) & (SalarySlip.month == month)
        )
        result = await self.db.exec(statement)
        return result.first()

    async def get_slips_by_employee(self, employee_id: uuid.UUID) -> list[SalarySlip]:
        statement = select(SalarySlip).where(SalarySlip.employee_id == employee_id).order_by(SalarySlip.month)
        result = await self.db.exec(statement)
        return list(result.all())

    async def get_slips_by_financial_year(self, employee_id: uuid.UUID, start_month: str, end_month: str) -> list[SalarySlip]:
        """Fetch slips matching range YYYY-MM (e.g. 2025-07 to 2026-06)."""
        statement = (
            select(SalarySlip)
            .where(
                (SalarySlip.employee_id == employee_id)
                & (SalarySlip.month >= start_month)
                & (SalarySlip.month <= end_month)
            )
            .order_by(SalarySlip.month)
        )
        result = await self.db.exec(statement)
        return list(result.all())

    async def create_slip(self, employee_id: uuid.UUID, slip_create: SalarySlipCreate) -> SalarySlip:
        db_slip = SalarySlip(
            employee_id=employee_id,
            month=slip_create.month,
            basic_salary=slip_create.basic_salary,
            house_rent=slip_create.house_rent,
            medical_allowance=slip_create.medical_allowance,
            conveyance=slip_create.conveyance,
            festival_bonus=slip_create.festival_bonus,
            provident_fund=slip_create.provident_fund,
            employer_provident_fund=slip_create.employer_provident_fund,
            other_allowances=slip_create.other_allowances,
            tax_deducted=slip_create.tax_deducted
        )
        self.db.add(db_slip)
        await self.db.flush()
        return db_slip

    async def update_slip(self, db_slip: SalarySlip, slip_update: SalarySlipUpdate) -> SalarySlip:
        update_data = slip_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_slip, key, value)
        self.db.add(db_slip)
        await self.db.flush()
        return db_slip

    async def delete_slip(self, db_slip: SalarySlip) -> None:
        await self.db.delete(db_slip)
        await self.db.flush()

    # Annual Certificate Methods
    async def get_certificate_by_id(self, cert_id: uuid.UUID) -> SalaryCertificate | None:
        statement = select(SalaryCertificate).where(SalaryCertificate.id == cert_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_certificates_by_employee(self, employee_id: uuid.UUID) -> list[SalaryCertificate]:
        statement = select(SalaryCertificate).where(SalaryCertificate.employee_id == employee_id)
        result = await self.db.exec(statement)
        return list(result.all())

    async def create_certificate(
        self,
        employee_id: uuid.UUID,
        financial_year: str,
        file_path: str,
        file_name: str
    ) -> SalaryCertificate:
        db_cert = SalaryCertificate(
            employee_id=employee_id,
            financial_year=financial_year,
            file_path=file_path,
            file_name=file_name,
            status="Pending"
        )
        self.db.add(db_cert)
        await self.db.flush()
        return db_cert

    async def update_certificate(self, db_cert: SalaryCertificate, updates: dict) -> SalaryCertificate:
        for key, value in updates.items():
            setattr(db_cert, key, value)
        self.db.add(db_cert)
        await self.db.flush()
        return db_cert

    async def delete_certificate(self, db_cert: SalaryCertificate) -> None:
        await self.db.delete(db_cert)
        await self.db.flush()
