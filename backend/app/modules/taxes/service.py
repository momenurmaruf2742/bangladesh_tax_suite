import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.modules.employees.repository import EmployeeRepository
from app.modules.investments.repository import InvestmentRepository
from app.modules.salaries.repository import SalaryRepository
from app.modules.taxes.model import TaxCalculation
from app.modules.taxes.repository import TaxRepository
from app.modules.taxes.schema import (
    TaxCalculationResponse,
    TaxDetailsResponse,
    TaxSlabBreakdown,
)
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class TaxService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TaxRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.salary_repo = SalaryRepository(db)
        self.invest_repo = InvestmentRepository(db)

    async def _get_employee(self, user_id: uuid.UUID):
        """Fetch employee profile or raise exception."""
        employee = await self.employee_repo.get_by_user_id(user_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee profile not setup. Please configure employee details first.",
            )
        return employee

    async def _get_applicable_rules(self, financial_year: str) -> dict:
        """Retrieve tax rules for a financial year from DB, with seeding and local fallback."""
        from app.core.tax_rules import get_tax_rules
        from app.modules.taxes.model import TaxRule
        from app.modules.taxes.repository import TaxRuleRepository

        rule_repo = TaxRuleRepository(self.db)
        db_rule = await rule_repo.get_by_year(financial_year)
        if db_rule:
            # Map DB TaxRule to the expected dict structure
            return {
                "exemption_rate": db_rule.exemption_rate,
                "exemption_max": db_rule.exemption_max,
                "dps_max": db_rule.dps_max,
                "rebate_rate": db_rule.rebate_rate,
                "income_rebate_limit_rate": db_rule.income_rebate_limit_rate,
                "max_rebate_cap": db_rule.max_rebate_cap,
                "max_eligible_invest_rate": db_rule.max_eligible_invest_rate,
                "max_eligible_invest_cap": db_rule.max_eligible_invest_cap,
                "thresholds": {
                    k: Decimal(str(v)) for k, v in db_rule.thresholds.items()
                },
                "slabs": [
                    (
                        slab[0],
                        Decimal(str(slab[1])) if slab[1] is not None else None,
                        Decimal(str(slab[2])),
                    )
                    for slab in db_rule.slabs
                ],
                "minimum_tax_location_based": db_rule.minimum_tax_location_based,
                "minimum_tax": {
                    k: Decimal(str(v)) for k, v in db_rule.minimum_tax.items()
                },
            }

        # Fallback to local python config
        local_rules = get_tax_rules(financial_year)

        # Seed the DB so it exists for editing / customization
        try:
            serialized_slabs = []
            for name, value, rate in local_rules["slabs"]:
                val_float = float(value) if value is not None else None
                rate_float = float(rate)
                serialized_slabs.append([name, val_float, rate_float])

            serialized_thresholds = {
                k: float(v) for k, v in local_rules["thresholds"].items()
            }
            serialized_min_tax = {
                k: float(v) for k, v in local_rules["minimum_tax"].items()
            }

            new_db_rule = TaxRule(
                financial_year=financial_year,
                exemption_rate=local_rules["exemption_rate"],
                exemption_max=local_rules["exemption_max"],
                dps_max=local_rules["dps_max"],
                rebate_rate=local_rules["rebate_rate"],
                income_rebate_limit_rate=local_rules["income_rebate_limit_rate"],
                max_rebate_cap=local_rules["max_rebate_cap"],
                max_eligible_invest_rate=local_rules["max_eligible_invest_rate"],
                max_eligible_invest_cap=local_rules["max_eligible_invest_cap"],
                thresholds=serialized_thresholds,
                slabs=serialized_slabs,
                minimum_tax_location_based=local_rules["minimum_tax_location_based"],
                minimum_tax=serialized_min_tax,
            )
            await rule_repo.create(new_db_rule)
        except Exception as e:
            print(f"Notice: Failed to seed dynamic rules for {financial_year}: {e}")

        return local_rules

    async def calculate_tax(
        self,
        user_id: uuid.UUID,
        financial_year: str,
        other_income: Decimal = Decimal("0.0"),
    ) -> TaxDetailsResponse:
        """Calculate tax details without persisting to database."""
        employee = await self._get_employee(user_id)
        employee_id = employee.id

        # 1. Fetch Salary data
        # Check if there is a verified salary certificate first
        certs = await self.salary_repo.get_certificates_by_employee(employee_id)
        active_cert = None
        for c in certs:
            if c.financial_year == financial_year and c.status == "Verified":
                active_cert = c
                break

        total_salary = Decimal("0.0")
        tds_salary = Decimal("0.0")
        pf_salary = Decimal("0.0")

        if active_cert:
            # Calculate from certificate
            total_salary = (
                active_cert.total_basic
                + active_cert.total_house_rent
                + active_cert.total_medical
                + active_cert.total_conveyance
                + active_cert.total_bonus
                + active_cert.total_others
            )
            tds_salary = active_cert.total_tax_deducted
            # Both employee and employer PF contributions are rebate eligible
            # Let's count the total PF from certificate (or double it if only employee side was logged)
            pf_salary = active_cert.total_provident_fund * 2
        else:
            # Fallback: calculate from monthly slips
            try:
                parts = financial_year.split("-")
                start_month = f"{parts[0]}-07"
                end_month = f"{parts[1]}-06"
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid financial year format. Must be YYYY-YYYY (e.g. 2025-2026)",
                )

            slips = await self.salary_repo.get_slips_by_financial_year(
                employee_id, start_month, end_month
            )
            for s in slips:
                # Total salary includes basic, house rent, medical, conveyance, bonus, other allowances, and employer PF match
                total_salary += (
                    s.basic_salary
                    + s.house_rent
                    + s.medical_allowance
                    + s.conveyance
                    + s.festival_bonus
                    + s.other_allowances
                    + s.employer_provident_fund
                )
                tds_salary += s.tax_deducted
                pf_salary += s.provident_fund + s.employer_provident_fund

        # Get tax rules dynamically from database with fallback & seeding
        rules = await self._get_applicable_rules(financial_year)

        # 2. Exemption Calculation (Salaried income: 1/3 of total salary or 4,50,000 BDT, whichever is lower)
        exempted_salary = min(
            total_salary / rules["exemption_rate"], rules["exemption_max"]
        )
        taxable_salary = max(Decimal("0.0"), total_salary - exempted_salary)

        # Total taxable income
        total_taxable_income = taxable_salary + other_income

        # 3. Determine Tax-Free Threshold
        threshold = rules["thresholds"]["default"]
        if employee.is_freedom_fighter:
            threshold = rules["thresholds"]["is_freedom_fighter"]
        elif employee.is_disabled:
            threshold = rules["thresholds"]["is_disabled"]
        elif employee.gender in rules["thresholds"]:
            threshold = rules["thresholds"][employee.gender]

        # 4. Slab-by-slab tax calculation
        remaining_income = total_taxable_income
        slabs_breakdown = []
        gross_tax = Decimal("0.0")

        # First tax-free slab
        tax_free_allotted = min(remaining_income, threshold)
        slabs_breakdown.append(
            TaxSlabBreakdown(
                slab_name=f"Tax-free limit ({int(threshold):,} BDT)",
                tax_rate=0.0,
                taxable_amount=tax_free_allotted,
                tax_amount=Decimal("0.0"),
            )
        )
        remaining_income -= tax_free_allotted

        # Progressive slabs
        for name, limit, rate in rules["slabs"][1:]:
            if remaining_income <= 0:
                break
            if limit is None:
                # Remaining balance
                tax_val = remaining_income * rate
                gross_tax += tax_val
                slabs_breakdown.append(
                    TaxSlabBreakdown(
                        slab_name=name,
                        tax_rate=float(rate),
                        taxable_amount=remaining_income,
                        tax_amount=tax_val,
                    )
                )
                remaining_income = Decimal("0.0")
            else:
                allotted = min(remaining_income, limit)
                tax_val = allotted * rate
                gross_tax += tax_val
                slabs_breakdown.append(
                    TaxSlabBreakdown(
                        slab_name=name,
                        tax_rate=float(rate),
                        taxable_amount=allotted,
                        tax_amount=tax_val,
                    )
                )
                remaining_income -= allotted

        # 5. Investment & Rebate calculation (Income Tax Act 2023, Section 78)
        # Fetch logged investments
        invest_logs = await self.invest_repo.get_investments_by_employee(employee_id)

        # Apply category specific limits (e.g. DPS allowable limit is 1,20,000 BDT/year under NBR rules)
        logged_investments = Decimal("0.0")
        for inv in invest_logs:
            if inv.financial_year == financial_year:
                if inv.category == "DPS":
                    logged_investments += min(inv.amount, rules["dps_max"])
                else:
                    logged_investments += inv.amount

        # Total invested includes actual logged investments + PF contributions from salary
        total_invested = logged_investments + pf_salary

        # Max eligible investment for rebate
        max_eligible_invest = min(
            total_taxable_income * rules["max_eligible_invest_rate"],
            rules["max_eligible_invest_cap"],
        )
        eligible_investment = min(total_invested, max_eligible_invest)

        # Rebate is lower of:
        # 1. rebate_rate of eligible investment
        # 2. income_rebate_limit_rate of total taxable income
        # 3. max_rebate_cap
        rebate_by_invest = eligible_investment * rules["rebate_rate"]
        rebate_by_income = total_taxable_income * rules["income_rebate_limit_rate"]

        investment_rebate = min(
            rebate_by_invest, rebate_by_income, rules["max_rebate_cap"]
        )

        # 6. Minimum Tax rule
        minimum_tax = Decimal("0.0")
        net_tax = Decimal("0.0")

        if gross_tax > 0:
            # Determine minimum tax by location
            if rules["minimum_tax_location_based"]:
                loc = employee.location
                if loc in rules["minimum_tax"]:
                    minimum_tax = rules["minimum_tax"][loc]
                else:
                    minimum_tax = rules["minimum_tax"]["default"]
            else:
                minimum_tax = rules["minimum_tax"]["default"]

            tax_after_rebate = max(Decimal("0.0"), gross_tax - investment_rebate)
            net_tax = max(tax_after_rebate, minimum_tax)

        # 7. Adjust with AIT and TDS
        # Fetch logged AIT records
        ait_logs = await self.invest_repo.get_aits_by_employee(employee_id)
        ait_paid = sum(
            ait.amount for ait in ait_logs if ait.financial_year == financial_year
        )

        # Final payable = Net Tax - AIT - TDS
        final_payable = net_tax - ait_paid - tds_salary

        summary = TaxCalculationResponse(
            id=uuid.uuid4(),  # Mock ID for temporary calculation
            employee_id=employee_id,
            financial_year=financial_year,
            total_salary=total_salary,
            exempted_salary=exempted_salary,
            taxable_salary=taxable_salary,
            other_income=other_income,
            total_taxable_income=total_taxable_income,
            gross_tax=gross_tax,
            total_invested=total_invested,
            eligible_investment=eligible_investment,
            investment_rebate=investment_rebate,
            minimum_tax=minimum_tax,
            net_tax=net_tax,
            ait_paid=ait_paid,
            tds_salary=tds_salary,
            final_payable=final_payable,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        return TaxDetailsResponse(
            summary=summary,
            slabs=slabs_breakdown,
            employee_gender=employee.gender,
            employee_location=employee.location,
            is_disabled=employee.is_disabled,
            is_freedom_fighter=employee.is_freedom_fighter,
        )

    async def calculate_and_save_tax(
        self,
        user_id: uuid.UUID,
        financial_year: str,
        other_income: Decimal = Decimal("0.0"),
    ) -> TaxDetailsResponse:
        """Calculate and persist the tax calculation in the database."""
        details = await self.calculate_tax(user_id, financial_year, other_income)
        employee = await self._get_employee(user_id)

        # Check if a calculation already exists for this employee and year
        existing = await self.repo.get_by_employee_and_year(employee.id, financial_year)
        if existing:
            # Delete old calculation to overwrite
            await self.repo.delete(existing)

        # Create database record
        s = details.summary
        db_calc = TaxCalculation(
            employee_id=employee.id,
            financial_year=financial_year,
            total_salary=s.total_salary,
            exempted_salary=s.exempted_salary,
            taxable_salary=s.taxable_salary,
            other_income=s.other_income,
            total_taxable_income=s.total_taxable_income,
            gross_tax=s.gross_tax,
            total_invested=s.total_invested,
            eligible_investment=s.eligible_investment,
            investment_rebate=s.investment_rebate,
            minimum_tax=s.minimum_tax,
            net_tax=s.net_tax,
            ait_paid=s.ait_paid,
            tds_salary=s.tds_salary,
            final_payable=s.final_payable,
        )

        saved = await self.repo.create(employee.id, db_calc)

        # Map generated ID and attributes to response
        s.id = saved.id
        s.created_at = saved.created_at
        details.summary = s
        return details

    async def get_calculation_history(
        self, user_id: uuid.UUID
    ) -> list[TaxCalculationResponse]:
        """Retrieve calculation runs history."""
        employee = await self._get_employee(user_id)
        calcs = await self.repo.get_history_by_employee(employee.id)
        return [TaxCalculationResponse.model_validate(c) for c in calcs]

    async def delete_calculation_run(
        self, user_id: uuid.UUID, calc_id: uuid.UUID
    ) -> None:
        """Delete a saved tax calculation run."""
        employee = await self._get_employee(user_id)
        calc = await self.repo.get_by_id(calc_id)
        if not calc or calc.employee_id != employee.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax calculation history record not found",
            )
        await self.repo.delete(calc)

    async def get_calculation_details(
        self, user_id: uuid.UUID, calc_id: uuid.UUID
    ) -> TaxDetailsResponse:
        """Fetch calculation details by ID, verifying ownership."""
        employee = await self._get_employee(user_id)
        calc = await self.repo.get_by_id(calc_id)
        if not calc or calc.employee_id != employee.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax calculation record not found",
            )

        details = await self.calculate_tax(
            user_id, calc.financial_year, calc.other_income
        )
        details.summary.id = calc.id
        details.summary.created_at = calc.created_at
        return details

    def generate_return_html(self, details: TaxDetailsResponse) -> str:
        """Generate a printable HTML string representing NBR Form IT-1152023."""
        s = details.summary
        try:
            parts = s.financial_year.split("-")
            income_year = f"{int(parts[0])-1}-{int(parts[1])-1}"
        except Exception:
            income_year = "Previous Year"

        def currency_str(val):
            return f"{float(val):,.2f} BDT" if val else "0.00 BDT"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>NBR Income Tax Return Form - IT-1152023</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f3f4f6;
            margin: 0;
            padding: 20px;
            color: #1f2937;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #ffffff;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border-radius: 8px;
            padding: 40px;
            border: 1px solid #e5e7eb;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #10b981;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            color: #065f46;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .header h2 {{
            margin: 5px 0 0 0;
            font-size: 16px;
            color: #374151;
            font-weight: 600;
        }}
        .header p {{
            margin: 5px 0 0 0;
            font-size: 13px;
            color: #6b7280;
        }}
        .badge-container {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 10px;
        }}
        .badge {{
            background-color: #ecfdf5;
            color: #047857;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            border: 1px solid #a7f3d0;
        }}
        .section-title {{
            font-size: 15px;
            font-weight: bold;
            color: #0f172a;
            border-left: 4px solid #10b981;
            padding-left: 10px;
            margin-top: 25px;
            margin-bottom: 12px;
            text-transform: uppercase;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px 30px;
            background-color: #f8fafc;
            padding: 15px 20px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            font-size: 13px;
        }}
        .info-item {{
            display: flex;
            justify-content: space-between;
            border-bottom: 1px dashed #e2e8f0;
            padding-bottom: 5px;
        }}
        .info-label {{
            color: #64748b;
            font-weight: 500;
        }}
        .info-value {{
            color: #0f172a;
            font-weight: 600;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 10px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f1f5f9;
            color: #475569;
            font-weight: 600;
        }}
        .text-right {{
            text-align: right;
        }}
        .font-mono {{
            font-family: monospace;
            font-size: 13px;
        }}
        .bold {{
            font-weight: bold;
            color: #0f172a;
        }}
        .refund {{
            color: #059669;
        }}
        .payable {{
            color: #dc2626;
        }}
        .footer-declaration {{
            margin-top: 40px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
            font-size: 12px;
            color: #475569;
            line-height: 1.6;
        }}
        .signature-area {{
            margin-top: 50px;
            display: flex;
            justify-content: space-between;
            font-size: 13px;
        }}
        .signature-line {{
            border-top: 1px solid #94a3b8;
            width: 200px;
            text-align: center;
            padding-top: 5px;
            color: #475569;
        }}
        .print-btn {{
            display: block;
            width: 120px;
            margin: 20px auto 0 auto;
            padding: 10px;
            background-color: #10b981;
            color: white;
            text-align: center;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: background-color 0.2s;
        }}
        .print-btn:hover {{
            background-color: #059669;
        }}
        @media print {{
            body {{
                background-color: #ffffff;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                border: none;
                padding: 0;
                max-width: 100%;
            }}
            .print-btn {{
                display: none;
            }}
            @page {{
                size: A4;
                margin: 15mm;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <button class="print-btn" onclick="window.print()">Print Form</button>

        <div class="header">
            <h1>National Board of Revenue</h1>
            <h2>Bangladesh Individual Income Tax Return Form (IT-1152023)</h2>
            <p>Under Section 82 of the Income Tax Act, 2023</p>
            <div class="badge-container">
                <div class="badge">Assessment Year: {s.financial_year}</div>
                <div class="badge">Income Year: {income_year}</div>
            </div>
        </div>

        <div class="section-title">A. Personal Information</div>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Taxpayer Name</span>
                <span class="info-value">Individual Taxpayer</span>
            </div>
            <div class="info-item">
                <span class="info-label">Gender</span>
                <span class="info-value">{details.employee_gender}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Tax Zone</span>
                <span class="info-value">Zone {details.summary.id != None and "01" or "--"}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Tax Circle</span>
                <span class="info-value">Circle {details.summary.id != None and "05" or "--"}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Location (Corp)</span>
                <span class="info-value">{details.employee_location}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Special Category</span>
                <span class="info-value">
                    { "Freedom Fighter" if details.is_freedom_fighter else "Disabled" if details.is_disabled else "General" }
                </span>
            </div>
        </div>

        <div class="section-title">B. Particulars of Taxable Income & Rebates</div>
        <table>
            <thead>
                <tr>
                    <th>Serial</th>
                    <th>Heads of Income</th>
                    <th class="text-right">Gross Amount</th>
                    <th class="text-right">Exempted Amount</th>
                    <th class="text-right">Taxable Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="bold">01</td>
                    <td class="bold">Income from Salaries</td>
                    <td class="text-right font-mono">{currency_str(s.total_salary)}</td>
                    <td class="text-right font-mono">{currency_str(s.exempted_salary)}</td>
                    <td class="text-right font-mono bold">{currency_str(s.taxable_salary)}</td>
                </tr>
                <tr>
                    <td class="bold">02</td>
                    <td class="bold">Income from Other Sources</td>
                    <td class="text-right font-mono">{currency_str(s.other_income)}</td>
                    <td class="text-right font-mono">0.00 BDT</td>
                    <td class="text-right font-mono bold">{currency_str(s.other_income)}</td>
                </tr>
                <tr style="background-color: #f8fafc;">
                    <td class="bold" colspan="2">Total Taxable Income (01 + 02)</td>
                    <td class="text-right font-mono">--</td>
                    <td class="text-right font-mono">--</td>
                    <td class="text-right font-mono bold" style="font-size: 14px; border-bottom: 2px double #64748b;">
                        {currency_str(s.total_taxable_income)}
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="section-title">C. Tax Computations & Outstanding Balance</div>
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th class="text-right">Amount (BDT)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Gross Tax Liability (as per progressive slabs)</td>
                    <td class="text-right font-mono">{currency_str(s.gross_tax)}</td>
                </tr>
                <tr>
                    <td>Investment Rebate (under Section 78)</td>
                    <td class="text-right font-mono text-emerald-600">- {currency_str(s.investment_rebate)}</td>
                </tr>
                <tr>
                    <td>Minimum Tax Applicability Limit</td>
                    <td class="text-right font-mono">{currency_str(s.minimum_tax)}</td>
                </tr>
                <tr style="background-color: #f8fafc;">
                    <td class="bold">Net Tax Liability</td>
                    <td class="text-right font-mono bold">{currency_str(s.net_tax)}</td>
                </tr>
                <tr>
                    <td>Source Tax (TDS on Salary)</td>
                    <td class="text-right font-mono">- {currency_str(s.tds_salary)}</td>
                </tr>
                <tr>
                    <td>Advance Income Tax (AIT) Paid</td>
                    <td class="text-right font-mono text-emerald-600">- {currency_str(s.ait_paid)}</td>
                </tr>
                <tr style="background-color: #f1f5f9;">
                    <td class="bold" style="font-size: 14px;">
                        { "Refundable Tax Amount" if s.final_payable < 0 else "Net Tax Payable" }
                    </td>
                    <td class="text-right font-mono bold { 'refund' if s.final_payable < 0 else 'payable' }" style="font-size: 15px; border-bottom: 2px double #475569;">
                        {currency_str(abs(s.final_payable))}
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="footer-declaration">
            <p><strong>Declaration:</strong> I solemnly declare that to the best of my knowledge and belief, the information given in this return and the statements and documents annexed herewith are correct and complete in accordance with the provisions of the Income Tax Act, 2023.</p>
        </div>

        <div class="signature-area">
            <div>
                <p>Date: ________________________</p>
                <p>Place: _______________________</p>
            </div>
            <div class="signature-line">
                Signature of Taxpayer
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
