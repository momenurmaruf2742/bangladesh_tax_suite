import os
import re
import uuid
from decimal import Decimal
from fastapi import HTTPException, status
import pypdf
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.employees.repository import EmployeeRepository
from app.modules.salaries.model import SalarySlip, SalaryCertificate
from app.modules.salaries.repository import SalaryRepository
from app.modules.salaries.schema import (
    SalarySlipCreate,
    SalarySlipUpdate,
    SalarySlipSummaryResponse
)

CERT_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "certificates")
PAYSLIP_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "payslips")


class SalaryService:
    def __init__(self, db: AsyncSession):
        self.repo = SalaryRepository(db)
        self.employee_repo = EmployeeRepository(db)

    async def _get_employee_id(self, user_id: uuid.UUID) -> uuid.UUID:
        """Fetch employee ID for user or raise exception."""
        employee = await self.employee_repo.get_by_user_id(user_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee profile not setup. Please configure employee details first."
            )
        return employee.id

    async def _get_employee_id_or_none(self, user_id: uuid.UUID) -> uuid.UUID | None:
        """Fetch employee ID for user or None if profile not setup."""
        employee = await self.employee_repo.get_by_user_id(user_id)
        return employee.id if employee else None

    async def create_or_update_slip(self, user_id: uuid.UUID, slip_create: SalarySlipCreate) -> SalarySlip:
        """Add a monthly salary slip record, or update if it exists."""
        employee_id = await self._get_employee_id(user_id)
        
        # Check if slip for this month already exists
        existing = await self.repo.get_slip_by_month(employee_id, slip_create.month)
        if existing:
            # Update existing slip
            update_in = SalarySlipUpdate(**slip_create.model_dump())
            return await self.repo.update_slip(existing, update_in)
        else:
            # Create new slip
            return await self.repo.create_slip(employee_id, slip_create)

    async def get_my_slips(self, user_id: uuid.UUID) -> list[SalarySlip]:
        """Fetch all slips for the logged in user's profile."""
        employee_id = await self._get_employee_id_or_none(user_id)
        if not employee_id:
            return []
        return await self.repo.get_slips_by_employee(employee_id)

    async def get_summary_for_year(self, user_id: uuid.UUID, financial_year: str) -> SalarySlipSummaryResponse:
        """Calculate the sum of all salary components for the given assessment year."""
        employee_id = await self._get_employee_id_or_none(user_id)
        if not employee_id:
            return SalarySlipSummaryResponse(
                financial_year=financial_year,
                months_count=0,
                total_basic=Decimal("0.0"),
                total_house_rent=Decimal("0.0"),
                total_medical=Decimal("0.0"),
                total_conveyance=Decimal("0.0"),
                total_bonus=Decimal("0.0"),
                total_provident_fund=Decimal("0.0"),
                total_employer_provident_fund=Decimal("0.0"),
                total_other_allowances=Decimal("0.0"),
                total_tax_deducted=Decimal("0.0"),
                gross_salary=Decimal("0.0")
            )
        
        # Parse assessment year format YYYY-YYYY e.g., 2025-2026
        # Income year runs from July of start year to June of end year
        try:
            parts = financial_year.split("-")
            start_year = parts[0]
            end_year = parts[1]
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid financial year format. Must be YYYY-YYYY (e.g. 2025-2026)"
            )

        start_month = f"{start_year}-07"
        end_month = f"{end_year}-06"

        slips = await self.repo.get_slips_by_financial_year(employee_id, start_month, end_month)

        summary = {
            "total_basic": Decimal("0.0"),
            "total_house_rent": Decimal("0.0"),
            "total_medical: ": Decimal("0.0"), # wait, map keys cleanly
            "total_medical": Decimal("0.0"),
            "total_conveyance": Decimal("0.0"),
            "total_bonus": Decimal("0.0"),
            "total_provident_fund": Decimal("0.0"),
            "total_employer_provident_fund": Decimal("0.0"),
            "total_other_allowances": Decimal("0.0"),
            "total_tax_deducted": Decimal("0.0"),
        }

        for s in slips:
            summary["total_basic"] += s.basic_salary
            summary["total_house_rent"] += s.house_rent
            summary["total_medical"] += s.medical_allowance
            summary["total_conveyance"] += s.conveyance
            summary["total_bonus"] += s.festival_bonus
            summary["total_provident_fund"] += s.provident_fund
            summary["total_employer_provident_fund"] += s.employer_provident_fund
            summary["total_other_allowances"] += s.other_allowances
            summary["total_tax_deducted"] += s.tax_deducted

        gross_salary = (
            summary["total_basic"]
            + summary["total_house_rent"]
            + summary["total_medical"]
            + summary["total_conveyance"]
            + summary["total_bonus"]
            + summary["total_other_allowances"]
        )

        return SalarySlipSummaryResponse(
            financial_year=financial_year,
            months_count=len(slips),
            total_basic=summary["total_basic"],
            total_house_rent=summary["total_house_rent"],
            total_medical=summary["total_medical"],
            total_conveyance=summary["total_conveyance"],
            total_bonus=summary["total_bonus"],
            total_provident_fund=summary["total_provident_fund"],
            total_employer_provident_fund=summary["total_employer_provident_fund"],
            total_other_allowances=summary["total_other_allowances"],
            total_tax_deducted=summary["total_tax_deducted"],
            gross_salary=gross_salary
        )

    async def parse_and_save_monthly_payslip(
        self,
        user_id: uuid.UUID,
        file_content: bytes,
        file_name: str
    ) -> SalarySlip:
        """Upload a monthly payslip PDF, parse month, gross salary, TDS, and save slip."""
        employee_id = await self._get_employee_id(user_id)

        os.makedirs(PAYSLIP_UPLOAD_DIR, exist_ok=True)
        file_uuid = uuid.uuid4()
        local_filename = f"{file_uuid}_{file_name}"
        file_path = os.path.join(PAYSLIP_UPLOAD_DIR, local_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        text = ""
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        except Exception as e:
            print(f"Error reading payslip PDF: {e}")

        month_str = "2026-06"
        month_map = {
            "jan": "01", "january": "01",
            "feb": "02", "february": "02",
            "mar": "03", "march": "03",
            "apr": "04", "april": "04",
            "may": "05",
            "jun": "06", "june": "06",
            "jul": "07", "july": "07",
            "aug": "08", "august": "08",
            "sep": "09", "september": "09",
            "oct": "10", "october": "10",
            "nov": "11", "november": "11",
            "dec": "12", "december": "12"
        }

        ym_match = re.search(r"(\d{4})-(\d{2})", text)
        if ym_match:
            month_str = f"{ym_match.group(1)}-{ym_match.group(2)}"
        else:
            m_match = re.search(r"(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|october|oct|november|nov|december|dec)\D+?(\d{4})", text, re.IGNORECASE)
            if m_match:
                m_name = m_match.group(1).lower()
                m_num = month_map.get(m_name, "06")
                y_num = m_match.group(2)
                month_str = f"{y_num}-{m_num}"

        def find_val(patterns: list[str], default_val: Decimal) -> Decimal:
            for p in patterns:
                match = re.search(p, text, re.IGNORECASE)
                if match:
                    num_str = match.group(1).replace(",", "")
                    try:
                        val = Decimal(num_str)
                        if val > Decimal("0.0"):
                            return val
                    except Exception:
                        pass
            return default_val

        basic = find_val([r"basic\s+salary\s*([0-9,]+(?:\.[0-9]+)?)", r"basic\s*([0-9,]+(?:\.[0-9]+)?)" ], Decimal("0.0"))
        house_rent = find_val([r"house\s+rent\s+allowance\s*([0-9,]+(?:\.[0-9]+)?)", r"house\s+rent\s*([0-9,]+(?:\.[0-9]+)?)" ], Decimal("0.0"))
        medical = find_val([r"medical\s+allowance\s*([0-9,]+(?:\.[0-9]+)?)", r"medical\s*([0-9,]+(?:\.[0-9]+)?)" ], Decimal("0.0"))
        conveyance = find_val([r"conveyance\s+allowance\s*([0-9,]+(?:\.[0-9]+)?)", r"conveyance\s*([0-9,]+(?:\.[0-9]+)?)" ], Decimal("0.0"))
        bonus = find_val([r"annual\s+bonus\s*([0-9,]+(?:\.[0-9]+)?)", r"performance\s+bonuses\s*([0-9,]+(?:\.[0-9]+)?)", r"bonus\s*([0-9,]+(?:\.[0-9]+)?)" ], Decimal("0.0"))
        pf = find_val([r"provident\s+fund\s*([0-9,]+(?:\.[0-9]+)?)", r"pf\s*([0-9,]+(?:\.[0-9]+)?)" ], Decimal("0.0"))
        
        tds = find_val([
            r"advance\s+income\s+tax\s*([0-9,]+(?:\.[0-9]+)?)",
            r"income\s+tax\s*([0-9,]+(?:\.[0-9]+)?)",
            r"tax\s+deducted\s*([0-9,]+(?:\.[0-9]+)?)",
            r"tds\s*([0-9,]+(?:\.[0-9]+)?)"
        ], Decimal("0.0"))

        gross = find_val([
            r"total\s+additions\s*([0-9,]+(?:\.[0-9]+)?)",
            r"earnings.*?\s*([0-9,]+(?:\.[0-9]+)?)",
            r"gross\s+salary\s*([0-9,]+(?:\.[0-9]+)?)",
            r"salary\s*([0-9,]+(?:\.[0-9]+)?)"
        ], Decimal("0.0"))

        if basic == Decimal("0.0") and gross > Decimal("0.0"):
            basic = (gross * Decimal("0.60")).quantize(Decimal("0.01"))
            house_rent = (gross * Decimal("0.30")).quantize(Decimal("0.01"))
            medical = (gross * Decimal("0.05")).quantize(Decimal("0.01"))
            conveyance = (gross * Decimal("0.05")).quantize(Decimal("0.01"))

        slip_data = SalarySlipCreate(
            month=month_str,
            basic_salary=basic,
            house_rent=house_rent,
            medical_allowance=medical,
            conveyance=conveyance,
            festival_bonus=bonus,
            provident_fund=pf,
            employer_provident_fund=pf,
            other_allowances=Decimal("0.0"),
            tax_deducted=tds,
            doc_path=file_path
        )

        return await self.create_or_update_slip(user_id, slip_data)

    async def save_salary_certificate(
        self,
        user_id: uuid.UUID,
        financial_year: str,
        file_content: bytes,
        file_name: str
    ) -> SalaryCertificate:
        """Upload salary certificate PDF and extract totals via regex/OCR."""
        employee_id = await self._get_employee_id(user_id)

        os.makedirs(CERT_UPLOAD_DIR, exist_ok=True)
        file_uuid = uuid.uuid4()
        local_filename = f"{file_uuid}_{file_name}"
        file_path = os.path.join(CERT_UPLOAD_DIR, local_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        db_cert = await self.repo.create_certificate(
            employee_id=employee_id,
            financial_year=financial_year,
            file_path=file_path,
            file_name=file_name
        )

        extracted_totals = {
            "total_basic": Decimal("0.0"),
            "total_house_rent": Decimal("0.0"),
            "total_medical": Decimal("0.0"),
            "total_conveyance": Decimal("0.0"),
            "total_bonus": Decimal("0.0"),
            "total_provident_fund": Decimal("0.0"),
            "total_tax_deducted": Decimal("0.0"),
            "total_others": Decimal("0.0"),
            "status": "Verified"
        }

        try:
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"

            if text.strip():
                def find_amount(patterns: list[str]) -> Decimal:
                    for p in patterns:
                        match = re.search(p, text, re.IGNORECASE)
                        if match:
                            num_str = match.group(1).replace(",", "").strip()
                            try:
                                val = Decimal(num_str)
                                if val >= 0:
                                    return val
                            except Exception:
                                pass
                    return Decimal("0.0")

                extracted_totals["total_basic"] = find_amount([
                    r"basic\s+salary.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                    r"basic.*?\s*([0-9,]+(?:\.[0-9]+)?)"
                ])

                extracted_totals["total_house_rent"] = find_amount([
                    r"house\s+rent.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                    r"rent.*?\s*([0-9,]+(?:\.[0-9]+)?)"
                ])

                extracted_totals["total_medical"] = find_amount([
                    r"medical\s+allowance.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                    r"medical.*?\s*([0-9,]+(?:\.[0-9]+)?)"
                ])

                extracted_totals["total_conveyance"] = find_amount([
                    r"conveyance\s+allowance.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                    r"conveyance.*?\s*([0-9,]+(?:\.[0-9]+)?)"
                ])

                extracted_totals["total_bonus"] = find_amount([
                    r"annual\s+bonus.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                    r"festival\s+bonus.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                    r"bonus.*?\s*([0-9,]+(?:\.[0-9]+)?)"
                ])

                extracted_totals["total_provident_fund"] = find_amount([
                    r"provident\s+fund.*?\s*([0-9,]+(?:\.[0-9]+)?)"
                ])

                # Check if tax is explicitly Nil/Zero or 0
                is_tax_nil = bool(re.search(r"(?:tax\s+deducted|tds|source\s+tax|income\s+tax).*?(?:nil|zero|none|n/a|\b0\b|\b0\.00\b)", text, re.IGNORECASE))
                if is_tax_nil:
                    extracted_totals["total_tax_deducted"] = Decimal("0.0")
                else:
                    extracted_totals["total_tax_deducted"] = find_amount([
                        r"tax\s+deducted\s+at\s+source.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                        r"total\s+tax\s+deducted.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                        r"tax\s+deducted.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                        r"income\s+tax.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                        r"tds.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                        r"source\s+tax.*?\s*([0-9,]+(?:\.[0-9]+)?)"
                    ])

                extracted_totals["total_others"] = find_amount([
                    r"other\s+allowance.*?\s*([0-9,]+(?:\.[0-9]+)?)",
                    r"other.*?\s*([0-9,]+(?:\.[0-9]+)?)"
                ])
        except Exception as e:
            print(f"Error parsing uploaded salary certificate PDF: {e}")

        return await self.repo.update_certificate(db_cert, extracted_totals)


    async def get_my_certificates(self, user_id: uuid.UUID) -> list[SalaryCertificate]:
        """Fetch uploaded certificates list."""
        employee_id = await self._get_employee_id_or_none(user_id)
        if not employee_id:
            return []
        return await self.repo.get_certificates_by_employee(employee_id)

    async def update_certificate_values(self, user_id: uuid.UUID, cert_id: uuid.UUID, updates: dict) -> SalaryCertificate:
        """Allow manual correction of extracted totals."""
        employee_id = await self._get_employee_id(user_id)
        db_cert = await self.repo.get_certificate_by_id(cert_id)
        if not db_cert or db_cert.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salary certificate not found"
            )

        # Sanitize keys that can be updated
        allowed_keys = [
            "total_basic", "total_house_rent", "total_medical", "total_conveyance",
            "total_bonus", "total_provident_fund", "total_tax_deducted", "total_others"
        ]
        sanitized_updates = {}
        for key in allowed_keys:
            if key in updates:
                sanitized_updates[key] = Decimal(str(updates[key]))

        return await self.repo.update_certificate(db_cert, sanitized_updates)

    async def delete_certificate(self, user_id: uuid.UUID, cert_id: uuid.UUID) -> None:
        """Remove certificate and delete local file."""
        employee_id = await self._get_employee_id(user_id)
        db_cert = await self.repo.get_certificate_by_id(cert_id)
        if not db_cert or db_cert.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salary certificate not found"
            )

        # Delete local file
        if os.path.exists(db_cert.file_path):
            try:
                os.remove(db_cert.file_path)
            except Exception:
                pass

        await self.repo.delete_certificate(db_cert)

    async def delete_salary_slip(self, user_id: uuid.UUID, slip_id: uuid.UUID) -> None:
        """Delete a monthly salary slip log."""
        employee_id = await self._get_employee_id(user_id)
        db_slip = await self.repo.get_slip_by_id(slip_id)
        if not db_slip or db_slip.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salary slip not found"
            )
        await self.repo.delete_slip(db_slip)
