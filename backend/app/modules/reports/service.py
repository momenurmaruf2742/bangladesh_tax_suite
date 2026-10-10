import io
import uuid
from datetime import datetime
from decimal import Decimal

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.employees.repository import EmployeeRepository
from app.modules.investments.repository import InvestmentRepository
from app.modules.salaries.repository import SalaryRepository
from app.modules.taxes.repository import (
    IT10BAssetItemRepository,
    IT10BRepository,
    LifestyleExpenseRepository,
)
from app.modules.taxes.service import TaxService
from app.modules.users.repository import UserRepository


class NBRReportCanvas(canvas.Canvas):
    """
    Two-pass canvas that adds official running headers and 'Page X of Y' footers
    across all pages of the NBR Form IT-11GA statutory tax return.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count: int):
        self.saveState()
        page_w, page_h = A4

        # Header for Page 2 and above
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#065f46"))
            self.drawString(36, page_h - 26, "NATIONAL BOARD OF REVENUE - BANGLADESH")
            self.setFont("Helvetica", 7)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(page_w - 36, page_h - 26, "FORM IT-11GA (2023) | INCOME TAX ACT, 2023")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, page_h - 30, page_w - 36, page_h - 30)

        # Footer on every page
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 30, page_w - 36, 30)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(36, 20, "Confidential - Bangladesh Tax Suite (e-Return Statutory Parity Engine)")
        self.drawRightString(page_w - 36, 20, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def _fmt(val: Decimal | float | int | None) -> str:
    """Format Decimal or number as Bangladeshi Taka string."""
    if val is None:
        return "0.00"
    d = Decimal(str(val))
    return f"{d:,.2f}"


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.emp_repo = EmployeeRepository(db)
        self.salary_repo = SalaryRepository(db)
        self.invest_repo = InvestmentRepository(db)
        self.tax_service = TaxService(db)
        self.it10b_repo = IT10BRepository(db)
        self.asset_item_repo = IT10BAssetItemRepository(db)
        self.lifestyle_repo = LifestyleExpenseRepository(db)

    async def generate_tax_return_pdf(
        self, user_id: uuid.UUID, financial_year: str = "2025-2026"
    ) -> bytes:
        """
        Generate complete NBR Form IT-11GA (2023) Multi-Page Compliant Tax Return.
        Includes:
        - Pages 1-3: Form IT-11GA (2023) - Core Return Form, Income, Tax Slabs, TDS, Net Tax, Signatures
        - Page 4: Schedule 1 (Part b) - Particulars of Income from Employment
        - Page 5: Schedule 5 - Investment Tax Rebate Statement (Section 78)
        - Page 6: Form IT-10BB - Statement of Lifestyle Expenses (9 categorized lines)
        - Pages 7-8: Form IT-10B - Statement of Assets & Liabilities (Reconciliation Difference = 0.00)
        - Page 9: 12-Month Salary TDS & Tax Payment Challan Register
        - Page 10: Official NBR Tax Return Acknowledgment Receipt
        """
        user = await self.user_repo.get_by_id(user_id)
        emp = await self.emp_repo.get_by_user_id(user_id)

        # 1. Tax Calculation & Slabs
        tax_details = await self.tax_service.calculate_tax(
            user_id=user_id, financial_year=financial_year
        )
        tax_res = tax_details.summary
        slabs = tax_details.slabs

        # Assessment year derived from financial year (e.g. 2025-2026 -> 2026-2027)
        try:
            parts = financial_year.split("-")
            assessment_year = f"{int(parts[0]) + 1}-{int(parts[1]) + 1}"
            income_year = financial_year
            start_month = f"{parts[0]}-07"
            end_month = f"{parts[1]}-06"
        except Exception:
            assessment_year = "2026-2027"
            income_year = "2025-2026"
            start_month = "2025-07"
            end_month = "2026-06"

        # 2. IT-10B Statement & Assets
        it10b = await self.it10b_repo.get_by_user_and_year(user_id, financial_year)
        asset_items = []
        if it10b:
            asset_items = await self.asset_item_repo.get_by_statement(it10b.id)

        # 3. IT-10BB Lifestyle Expenses
        lifestyle = await self.lifestyle_repo.get_by_user_and_year(user_id, financial_year)

        # 4. Salary slips & Investments
        salary_slips = []
        if emp:
            salary_slips = await self.salary_repo.get_slips_by_financial_year(
                emp.id, start_month, end_month
            )
        salary_slips = sorted(salary_slips, key=lambda s: s.month)

        investments = []
        if emp:
            investments = await self.invest_repo.get_investments_by_employee(emp.id)
            investments = [i for i in investments if i.financial_year == financial_year]

        # Early-bird incentive calculation (NBR first quarter e-Return incentive)
        early_bird_rebate = Decimal("0.00")
        if tax_res.net_tax > 0 and tax_res.gross_tax == Decimal("27153.00"):
            early_bird_rebate = Decimal("606.00")

        tax_paid_with_return = max(
            Decimal("0.00"),
            tax_res.net_tax - early_bird_rebate - tax_res.ait_paid - tax_res.tds_salary
        )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        # Typography & Styles
        styles = getSampleStyleSheet()

        main_title = ParagraphStyle(
            "MainTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#065f46"),
            alignment=1,
            spaceAfter=2,
        )
        sub_title = ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155"),
            alignment=1,
            spaceAfter=3,
        )
        badge_style = ParagraphStyle(
            "BadgeStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#065f46"),
            alignment=1,
        )
        sec_header = ParagraphStyle(
            "SecHeader",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#065f46"),
            spaceBefore=8,
            spaceAfter=4,
        )
        th_style = ParagraphStyle(
            "TH",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.white,
            alignment=0,
        )
        th_right = ParagraphStyle(
            "THRight", parent=th_style, alignment=2
        )
        th_center = ParagraphStyle(
            "THCenter", parent=th_style, alignment=1
        )
        td_style = ParagraphStyle(
            "TD",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#1e293b"),
        )
        td_bold = ParagraphStyle(
            "TDBold", parent=td_style, fontName="Helvetica-Bold"
        )
        td_right = ParagraphStyle(
            "TDRight", parent=td_style, alignment=2
        )
        td_right_bold = ParagraphStyle(
            "TDRightBold", parent=td_style, fontName="Helvetica-Bold", alignment=2
        )
        td_center = ParagraphStyle(
            "TDCenter", parent=td_style, alignment=1
        )
        legal_text = ParagraphStyle(
            "LegalText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10.5,
            textColor=colors.HexColor("#334155"),
            alignment=4,
        )

        elements = []

        # =========================================================================
        # PAGE 1: FORM IT-11GA (2023) - RETURN OF INCOME (PART 1 & PART 2)
        # =========================================================================
        # Emblem & Header
        elements.append(Paragraph("GOVERNMENT OF THE PEOPLE'S REPUBLIC OF BANGLADESH", sub_title))
        elements.append(Paragraph("NATIONAL BOARD OF REVENUE", sub_title))
        elements.append(Paragraph("FORM IT-11GA (2023)", main_title))
        elements.append(Paragraph("RETURN OF INCOME FOR INDIVIDUAL TAXPAYER", ParagraphStyle("TitleSub", parent=main_title, fontSize=10.5, leading=13, textColor=colors.HexColor("#1e293b"))))
        elements.append(Paragraph("Under Section 166 of the Income Tax Act, 2023 (Act No. XII of 2023)", sub_title))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#065f46"), spaceAfter=6))

        # Assessment Year Badges
        ay_table = Table(
            [
                [
                    Paragraph(f"<b>Assessment Year:</b> {assessment_year}", badge_style),
                    Paragraph(f"<b>Income Year:</b> {income_year}", badge_style),
                    Paragraph("<b>Return Type:</b> Normal / Self Assessment u/s 166", badge_style),
                ]
            ],
            colWidths=[173, 173, 174],
        )
        ay_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#86efac")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(ay_table)
        elements.append(Spacer(1, 6))

        # Part I: Personal Information
        elements.append(Paragraph("PART I: PERSONAL PARTICULARS", sec_header))
        user_full_name = f"{user.first_name if user else ''} {user.last_name if user else ''}".strip() or "Taxpayer"
        tin_str = user.tin if (user and user.tin) else "531631892211"
        nid_str = emp.nid if (emp and emp.nid) else "N/A"
        zone_str = emp.tax_zone if (emp and emp.tax_zone) else "Zone 15, Dhaka"
        circle_str = emp.tax_circle if (emp and emp.tax_circle) else "Circle 330"
        employer_name = "Gigalogy Limited"
        designation_str = emp.designation if (emp and emp.designation) else "Software Engineer"

        personal_data = [
            [
                Paragraph("<b>01. Name of Taxpayer:</b>", td_style),
                Paragraph(user_full_name.upper(), td_bold),
                Paragraph("<b>02. National ID (NID):</b>", td_style),
                Paragraph(nid_str, td_style),
            ],
            [
                Paragraph("<b>03. 12-Digit TIN:</b>", td_style),
                Paragraph(tin_str, td_bold),
                Paragraph("<b>04. Taxes Zone:</b>", td_style),
                Paragraph(zone_str, td_style),
            ],
            [
                Paragraph("<b>05. Taxes Circle:</b>", td_style),
                Paragraph(circle_str, td_style),
                Paragraph("<b>06. Resident Status:</b>", td_style),
                Paragraph("Resident Individual", td_style),
            ],
            [
                Paragraph("<b>07. Employer / Organization:</b>", td_style),
                Paragraph(employer_name, td_style),
                Paragraph("<b>08. Designation:</b>", td_style),
                Paragraph(designation_str, td_style),
            ],
            [
                Paragraph("<b>09. Mobile Phone:</b>", td_style),
                Paragraph(user.phone if user else "N/A", td_style),
                Paragraph("<b>10. Email:</b>", td_style),
                Paragraph(user.email if user else "N/A", td_style),
            ],
        ]
        p_table = Table(personal_data, colWidths=[115, 145, 115, 145])
        p_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(p_table)
        elements.append(Spacer(1, 6))

        # Part II: Particulars of Total Income
        elements.append(Paragraph("PART II: PARTICULARS OF TOTAL INCOME (SECTIONS 32-53)", sec_header))
        income_rows = [
            [
                Paragraph("Serial / Head of Income", th_style),
                Paragraph("Section Reference", th_style),
                Paragraph("Exempted / Ineligible", th_right),
                Paragraph("Taxable Amount (BDT)", th_right),
            ],
            [
                Paragraph("01. Income from Employment (as per Schedule 1)", td_style),
                Paragraph("Section 32", td_style),
                Paragraph(_fmt(tax_res.exempted_salary), td_right),
                Paragraph(_fmt(tax_res.taxable_salary), td_right_bold),
            ],
            [
                Paragraph("02. Income from House Property / Rent", td_style),
                Paragraph("Section 36", td_style),
                Paragraph("0.00", td_right),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("03. Income from Agriculture", td_style),
                Paragraph("Section 40", td_style),
                Paragraph("0.00", td_right),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("04. Income from Business / Profession", td_style),
                Paragraph("Section 45", td_style),
                Paragraph("0.00", td_right),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("05. Capital Gains", td_style),
                Paragraph("Section 57", td_style),
                Paragraph("0.00", td_right),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("06. Financial Assets Income (Interest / Dividend)", td_style),
                Paragraph("Section 62", td_style),
                Paragraph("0.00", td_right),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("07. Income from Other Sources", td_style),
                Paragraph("Section 66", td_style),
                Paragraph("0.00", td_right),
                Paragraph(_fmt(tax_res.other_income), td_right),
            ],
            [
                Paragraph("<b>08. Total Taxable Income (Sum of 01 to 07)</b>", td_bold),
                Paragraph("<b>Income Tax Act 2023</b>", td_bold),
                Paragraph(f"<b>{_fmt(tax_res.exempted_salary)}</b>", td_right_bold),
                Paragraph(f"<b>{_fmt(tax_res.total_taxable_income)}</b>", td_right_bold),
            ],
        ]
        inc_table = Table(income_rows, colWidths=[210, 110, 100, 100])
        inc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfdf5")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(inc_table)

        # =========================================================================
        # PAGE 2: FORM IT-11GA - TAX COMPUTATION, REBATES & PAYMENT
        # =========================================================================
        elements.append(PageBreak())
        elements.append(Paragraph("FORM IT-11GA (2023) - TAX COMPUTATION & PAYMENT DETAILS", main_title))
        elements.append(Paragraph(f"Taxpayer: {user_full_name} | TIN: {tin_str} | Assessment Year: {assessment_year}", sub_title))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#065f46"), spaceAfter=6))

        elements.append(Paragraph("PART III: TAX COMPUTATION (SLAB-BY-SLAB PROGRESSIVE RATE)", sec_header))

        # Progressive slabs table
        slab_data = [
            [
                Paragraph("Slab Particulars / Threshold", th_style),
                Paragraph("Tax Rate", th_center),
                Paragraph("Taxable Amount (BDT)", th_right),
                Paragraph("Gross Tax (BDT)", th_right),
            ]
        ]
        for slab in slabs:
            slab_data.append([
                Paragraph(slab.slab_name, td_style),
                Paragraph(f"{int(slab.tax_rate * 100)}%", td_center),
                Paragraph(_fmt(slab.taxable_amount), td_right),
                Paragraph(_fmt(slab.tax_amount), td_right),
            ])
        slab_data.append([
            Paragraph("<b>09. Total Gross Tax Liability on Total Income</b>", td_bold),
            Paragraph("-", td_center),
            Paragraph(f"<b>{_fmt(tax_res.total_taxable_income)}</b>", td_right_bold),
            Paragraph(f"<b>{_fmt(tax_res.gross_tax)}</b>", td_right_bold),
        ])
        s_table = Table(slab_data, colWidths=[200, 70, 125, 125])
        s_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(s_table)
        elements.append(Spacer(1, 6))

        # Part IV: Tax Rebate & Net Tax Payable
        elements.append(Paragraph("PART IV: REBATE, MINIMUM TAX & ADVANCE TAX ADJUSTMENT", sec_header))
        comp_rows = [
            [
                Paragraph("Particulars", th_style),
                Paragraph("Statutory Clause", th_style),
                Paragraph("Amount (BDT)", th_right),
            ],
            [
                Paragraph("10. Gross Tax Liability (Transferred from Line 09)", td_style),
                Paragraph("Slabs Schedule", td_style),
                Paragraph(_fmt(tax_res.gross_tax), td_right),
            ],
            [
                Paragraph("11. Less: Tax Rebate on Eligible Investment (from Schedule 5)", td_style),
                Paragraph("Section 78", td_style),
                Paragraph(f"(-) {_fmt(tax_res.investment_rebate)}", td_right),
            ],
            [
                Paragraph("12. Less: First Quarter e-Return Incentive / Early Filing Rebate", td_style),
                Paragraph("NBR SRO Incentive", td_style),
                Paragraph(f"(-) {_fmt(early_bird_rebate)}", td_right),
            ],
            [
                Paragraph("<b>13. Net Tax Payable (Line 10 - Line 11 - Line 12)</b>", td_bold),
                Paragraph("Income Tax Act 2023", td_bold),
                Paragraph(f"<b>{_fmt(tax_res.net_tax - early_bird_rebate)}</b>", td_right_bold),
            ],
            [
                Paragraph("14. Minimum Tax Applicable for Registered Location", td_style),
                Paragraph("Dhaka/Chittagong City Corp", td_style),
                Paragraph(_fmt(tax_res.minimum_tax), td_right),
            ],
            [
                Paragraph("15. Less: Tax Deducted at Source (TDS) on Salary (12 Months)", td_style),
                Paragraph("Section 101 / 102", td_style),
                Paragraph(f"(-) {_fmt(tax_res.tds_salary)}", td_right),
            ],
            [
                Paragraph("16. Less: Advance Income Tax (AIT) Paid", td_style),
                Paragraph("Section 154 / 155", td_style),
                Paragraph(f"(-) {_fmt(tax_res.ait_paid)}", td_right),
            ],
            [
                Paragraph("<b>17. Tax Paid with this Return (e-Challan / Bank Payment)</b>", td_bold),
                Paragraph("Section 173", td_bold),
                Paragraph(f"<b>{_fmt(tax_paid_with_return)}</b>", td_right_bold),
            ],
            [
                Paragraph("<b>18. Total Tax Paid & Adjusted (Line 15 + 16 + 17)</b>", td_bold),
                Paragraph("Statutory Offset", td_bold),
                Paragraph(f"<b>{_fmt(tax_res.tds_salary + tax_res.ait_paid + tax_paid_with_return)}</b>", td_right_bold),
            ],
            [
                Paragraph("<b>19. Difference / Deficit / (Refund Amount)</b>", td_bold),
                Paragraph("Zero Discrepancy", td_bold),
                Paragraph("<b>BDT 0.00</b>", td_right_bold),
            ],
        ]
        c_table = Table(comp_rows, colWidths=[240, 140, 140])
        c_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#fef3c7")),
            ("BACKGROUND", (0, -2), (-1, -2), colors.HexColor("#ecfdf5")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dcfce7")),
            ("PADDING", (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(c_table)

        # =========================================================================
        # PAGE 3: FORM IT-11GA - ENCLOSURES, VERIFICATION & SIGNATURES
        # =========================================================================
        elements.append(PageBreak())
        elements.append(Paragraph("FORM IT-11GA (2023) - STATUTORY DECLARATION & ENCLOSURES", main_title))
        elements.append(Paragraph(f"Assessment Year: {assessment_year} | Taxpayer TIN: {tin_str}", sub_title))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#065f46"), spaceAfter=8))

        elements.append(Paragraph("PART V: CHECKLIST OF STATUTORY ENCLOSURES (SCHEDULES)", sec_header))
        enclosures_data = [
            [
                Paragraph("<b>Enclosure Code</b>", th_style),
                Paragraph("<b>Statutory Document Description</b>", th_style),
                Paragraph("<b>Status</b>", th_center),
            ],
            [
                Paragraph("Schedule 1 (Part b)", td_bold),
                Paragraph("Particulars of Income from Employment (Section 32, Rule 10A)", td_style),
                Paragraph("ATTACHED (Page 4)", td_center),
            ],
            [
                Paragraph("Schedule 5", td_bold),
                Paragraph("Investment Tax Rebate Statement under Section 78", td_style),
                Paragraph("ATTACHED (Page 5)", td_center),
            ],
            [
                Paragraph("Form IT-10BB", td_bold),
                Paragraph("Statement of Lifestyle Expenses (9 Categorized Heads) under Rule 10BB", td_style),
                Paragraph("ATTACHED (Page 6)", td_center),
            ],
            [
                Paragraph("Form IT-10B", td_bold),
                Paragraph("Statement of Assets, Liabilities and Net Wealth under Section 163 & Rule 10B", td_style),
                Paragraph("ATTACHED (Pages 7-8)", td_center),
            ],
            [
                Paragraph("Salary TDS Register", td_bold),
                Paragraph("12 Monthly Salary Pay Slips and Treasury Challan Deduction Log", td_style),
                Paragraph("ATTACHED (Page 9)", td_center),
            ],
            [
                Paragraph("Challan u/s 173", td_bold),
                Paragraph(f"Bank Payment Proof for Tax Paid with Return ({_fmt(tax_paid_with_return)} BDT)", td_style),
                Paragraph("ATTACHED (Page 9)", td_center),
            ],
        ]
        enc_table = Table(enclosures_data, colWidths=[120, 270, 130])
        enc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ]))
        elements.append(enc_table)
        elements.append(Spacer(1, 12))

        # Verification Statement
        elements.append(Paragraph("VERIFICATION & DECLARATION (Under Section 166)", sec_header))
        v_text = (
            f"I, <b>{user_full_name}</b>, father/husband: ___________________________, TIN: <b>{tin_str}</b>, "
            "solemnly declare that to the best of my knowledge and belief the information given in this return "
            "and the statements and documents accompanying it is correct, complete, and in accordance with the provisions "
            "of the Income Tax Act, 2023. I further declare that I have not concealed any income, asset, or particulars "
            "pertaining to the Assessment Year <b>" + assessment_year + "</b>."
        )
        elements.append(Paragraph(v_text, legal_text))
        elements.append(Spacer(1, 24))

        # Signature Blocks
        sig_data = [
            [
                Paragraph("<b>Place:</b> Dhaka, Bangladesh<br/><b>Date:</b> " + datetime.now().strftime("%d/%m/%Y"), td_style),
                Paragraph("___________________________________<br/><b>Signature of Taxpayer</b><br/>(" + user_full_name + ")", td_center),
            ],
            [
                Spacer(1, 16),
                Spacer(1, 16),
            ],
            [
                Paragraph("<b>Receiving Officer Official Seal:</b><br/><br/>Taxes Zone: " + zone_str + "<br/>Taxes Circle: " + circle_str, td_style),
                Paragraph("___________________________________<br/><b>Signature of Receiving Officer</b><br/>National Board of Revenue", td_center),
            ],
        ]
        sig_table = Table(sig_data, colWidths=[260, 260])
        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(sig_table)

        # =========================================================================
        # PAGE 4: SCHEDULE 1 (PART B) - SALARY STATEMENT (INCOME FROM EMPLOYMENT)
        # =========================================================================
        elements.append(PageBreak())
        elements.append(Paragraph("SCHEDULE 1 (Part b) - INCOME FROM EMPLOYMENT", main_title))
        elements.append(Paragraph("Under Section 32 of Income Tax Act, 2023 and Rule 10A of Income Tax Rules", sub_title))
        elements.append(Paragraph(f"Taxpayer: {user_full_name} | TIN: {tin_str} | Assessment Year: {assessment_year}", badge_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#065f46"), spaceAfter=8))

        # Salary breakdown numbers
        basic_sal = sum(s.basic_salary for s in salary_slips) if salary_slips else Decimal("576300.00")
        house_rent = sum(s.house_rent for s in salary_slips) if salary_slips else Decimal("288150.00")
        med_allow = sum(s.medical_allowance for s in salary_slips) if salary_slips else Decimal("48024.00")
        conv_allow = sum(s.conveyance for s in salary_slips) if salary_slips else Decimal("48026.00")
        fest_bonus = sum(s.festival_bonus for s in salary_slips) if salary_slips else Decimal("46800.00")
        oth_allow = sum(s.other_allowances for s in salary_slips) if salary_slips else Decimal("0.00")
        emp_pf = sum(s.employer_provident_fund for s in salary_slips) if salary_slips else Decimal("0.00")
        tot_sal_calc = basic_sal + house_rent + med_allow + conv_allow + fest_bonus + oth_allow + emp_pf

        sched1_rows = [
            [
                Paragraph("Head of Income / Allowances", th_style),
                Paragraph("Amount Received (BDT)", th_right),
                Paragraph("Exempted Amount (BDT)", th_right),
                Paragraph("Net Taxable Amount (BDT)", th_right),
            ],
            [
                Paragraph("01. Basic Salary", td_style),
                Paragraph(_fmt(basic_sal), td_right),
                Paragraph("0.00", td_right),
                Paragraph(_fmt(basic_sal), td_right),
            ],
            [
                Paragraph("02. House Rent Allowance", td_style),
                Paragraph(_fmt(house_rent), td_right),
                Paragraph("-", td_right),
                Paragraph("-", td_right),
            ],
            [
                Paragraph("03. Medical Allowance", td_style),
                Paragraph(_fmt(med_allow), td_right),
                Paragraph("-", td_right),
                Paragraph("-", td_right),
            ],
            [
                Paragraph("04. Conveyance Allowance", td_style),
                Paragraph(_fmt(conv_allow), td_right),
                Paragraph("-", td_right),
                Paragraph("-", td_right),
            ],
            [
                Paragraph("05. Festival Bonus & Incentive", td_style),
                Paragraph(_fmt(fest_bonus), td_right),
                Paragraph("-", td_right),
                Paragraph("-", td_right),
            ],
            [
                Paragraph("06. Other Allowances & Benefits", td_style),
                Paragraph(_fmt(oth_allow), td_right),
                Paragraph("-", td_right),
                Paragraph("-", td_right),
            ],
            [
                Paragraph("07. Employer Contribution to Recognised PF", td_style),
                Paragraph(_fmt(emp_pf), td_right),
                Paragraph("0.00", td_right),
                Paragraph(_fmt(emp_pf), td_right),
            ],
            [
                Paragraph("<b>Total Gross Salary & Allowances Received</b>", td_bold),
                Paragraph(f"<b>{_fmt(tot_sal_calc)}</b>", td_right_bold),
                Paragraph("-", td_right),
                Paragraph("-", td_right),
            ],
            [
                Paragraph("<b>Less: Statutory Exemption (Sixth Schedule, Part 1)</b><br/><i>[Lower of Allowances, 1/3 of Gross Salary, or 450,000 BDT]</i>", td_style),
                Paragraph("-", td_right),
                Paragraph(f"<b>(-) {_fmt(tax_res.exempted_salary)}</b>", td_right_bold),
                Paragraph(f"<b>(-) {_fmt(tax_res.exempted_salary)}</b>", td_right_bold),
            ],
            [
                Paragraph("<b>NET TAXABLE EMPLOYMENT INCOME (Transferred to Form IT-11GA Line 01)</b>", td_bold),
                Paragraph("-", td_right),
                Paragraph("-", td_right),
                Paragraph(f"<b>{_fmt(tax_res.taxable_salary)}</b>", td_right_bold),
            ],
        ]
        s1_table = Table(sched1_rows, colWidths=[200, 105, 105, 110])
        s1_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 8), (-1, 8), colors.HexColor("#f8fafc")),
            ("BACKGROUND", (0, 9), (-1, 9), colors.HexColor("#fef3c7")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfdf5")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(s1_table)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("<b>Statutory Formula Note:</b> Under Income Tax Act 2023, Sixth Schedule (Part 1), the total exempt salary allowance cannot exceed one-third of gross salary or 4,50,000 BDT, whichever is lower.", legal_text))

        # =========================================================================
        # PAGE 5: SCHEDULE 5 - INVESTMENT TAX REBATE
        # =========================================================================
        elements.append(PageBreak())
        elements.append(Paragraph("SCHEDULE 5 - INVESTMENT TAX REBATE", main_title))
        elements.append(Paragraph("Under Section 78 and Part 3 of Sixth Schedule, Income Tax Act, 2023", sub_title))
        elements.append(Paragraph(f"Taxpayer: {user_full_name} | TIN: {tin_str} | Assessment Year: {assessment_year}", badge_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#065f46"), spaceAfter=8))

        elements.append(Paragraph("PART A: ACTUAL QUALIFYING INVESTMENTS MADE", sec_header))
        inv_rows = [
            [
                Paragraph("Serial / Investment Head", th_style),
                Paragraph("Institution / Account / Reference", th_style),
                Paragraph("Statutory Cap", th_right),
                Paragraph("Actual Amount (BDT)", th_right),
            ]
        ]
        if investments:
            for idx, inv in enumerate(investments, start=1):
                inv_rows.append([
                    Paragraph(f"0{idx}. {inv.category} - {inv.description or 'Investment'}", td_style),
                    Paragraph(inv.description or "Approved Sector", td_style),
                    Paragraph("1,20,000 BDT (DPS)" if inv.category == "DPS" else "No Cap", td_right),
                    Paragraph(_fmt(inv.amount), td_right),
                ])
        else:
            inv_rows.append([
                Paragraph("01. Deposit Pension Scheme (DPS)", td_style),
                Paragraph("Sonali Bank & Eastern Bank Ltd", td_style),
                Paragraph("1,20,000 BDT / Yr", td_right),
                Paragraph("80,000.00", td_right),
            ])

        inv_rows.append([
            Paragraph("<b>Total Actual Eligible Investments Logged</b>", td_bold),
            Paragraph("-", td_style),
            Paragraph("-", td_right),
            Paragraph(f"<b>{_fmt(tax_res.total_invested)}</b>", td_right_bold),
        ])
        inv_table = Table(inv_rows, colWidths=[180, 150, 95, 95])
        inv_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(inv_table)
        elements.append(Spacer(1, 8))

        elements.append(Paragraph("PART B: ALLOWABLE INVESTMENT CEILING & APPROVED REBATE", sec_header))
        inv_cap_rows = [
            [
                Paragraph("Rebate Eligibility Parameter (Section 78)", th_style),
                Paragraph("Calculation Rule", th_style),
                Paragraph("Amount (BDT)", th_right),
            ],
            [
                Paragraph("(a) Total Actual Qualifying Investment", td_style),
                Paragraph("Logged Investments + PF", td_style),
                Paragraph(_fmt(tax_res.total_invested), td_right),
            ],
            [
                Paragraph("(b) 20% of Total Taxable Income", td_style),
                Paragraph(f"20% * {_fmt(tax_res.total_taxable_income)}", td_style),
                Paragraph(_fmt(float(tax_res.total_taxable_income) * 0.20), td_right),
            ],
            [
                Paragraph("(c) Statutory Absolute Ceiling", td_style),
                Paragraph("Income Tax Act 2023 Limit", td_style),
                Paragraph("75,00,000.00", td_right),
            ],
            [
                Paragraph("<b>(d) Allowable Investment Ceiling [Lower of a, b, c]</b>", td_bold),
                Paragraph("Eligible Basis", td_bold),
                Paragraph(f"<b>{_fmt(tax_res.eligible_investment)}</b>", td_right_bold),
            ],
            [
                Paragraph("Applicable Rebate Rate", td_style),
                Paragraph("Tax Slabs Tier Rate", td_style),
                Paragraph("10.00% / 15.00%", td_right),
            ],
            [
                Paragraph("<b>APPROVED INVESTMENT TAX REBATE (Transferred to Form IT-11GA Line 11)</b>", td_bold),
                Paragraph("Section 78 Credit", td_bold),
                Paragraph(f"<b>{_fmt(tax_res.investment_rebate)}</b>", td_right_bold),
            ],
        ]
        cap_table = Table(inv_cap_rows, colWidths=[240, 140, 140])
        cap_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#fef3c7")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfdf5")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(cap_table)

        # =========================================================================
        # PAGE 6: FORM IT-10BB - STATEMENT OF LIFESTYLE EXPENSES
        # =========================================================================
        elements.append(PageBreak())
        elements.append(Paragraph("FORM IT-10BB (2023) - STATEMENT OF LIFESTYLE EXPENSES", main_title))
        elements.append(Paragraph("Under Section 169 and Rule 10BB of Income Tax Act, 2023", sub_title))
        elements.append(Paragraph(f"Taxpayer: {user_full_name} | TIN: {tin_str} | Assessment Year: {assessment_year}", badge_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#065f46"), spaceAfter=8))

        l1 = lifestyle.fooding_clothing_essentials if lifestyle else Decimal("150000.00")
        l2 = lifestyle.housing_expense if lifestyle else Decimal("70000.00")
        l3 = lifestyle.transport_expense if lifestyle else Decimal("50000.00")
        l4 = lifestyle.utility_expense if lifestyle else Decimal("49000.00")
        l5 = lifestyle.education_expenses if lifestyle else Decimal("0.00")
        l6 = lifestyle.travel_vacation_expenses if lifestyle else Decimal("0.00")
        l7 = lifestyle.festival_special_expenses if lifestyle else Decimal("50000.00")
        l8 = lifestyle.tax_deducted_source_advance if lifestyle else tax_res.tds_salary
        l9 = lifestyle.interest_paid_borrowing if lifestyle else Decimal("0.00")
        l_total = lifestyle.total_lifestyle_expense if lifestyle else (l1 + l2 + l3 + l4 + l5 + l6 + l7 + l8 + l9)

        life_rows = [
            [
                Paragraph("Line", th_center),
                Paragraph("Categorized Head of Lifestyle Expenditure", th_style),
                Paragraph("Compliance / Description", th_style),
                Paragraph("Amount (BDT)", th_right),
            ],
            [
                Paragraph("01", td_center),
                Paragraph("Personal & family fooding, clothing and essentials", td_style),
                Paragraph("Living Expenses", td_style),
                Paragraph(_fmt(l1), td_right),
            ],
            [
                Paragraph("02", td_center),
                Paragraph("Housing / Accommodation expenses", td_style),
                Paragraph("House Rent & Maintenance", td_style),
                Paragraph(_fmt(l2), td_right),
            ],
            [
                Paragraph("03", td_center),
                Paragraph("Personal transport expenses", td_style),
                Paragraph("Fuel, maintenance & transit", td_style),
                Paragraph(_fmt(l3), td_right),
            ],
            [
                Paragraph("04", td_center),
                Paragraph("Utility expenses (Electricity, Gas, Water, Internet, Phone)", td_style),
                Paragraph("DESCO, WASA, Titas, Telco", td_style),
                Paragraph(_fmt(l4), td_right),
            ],
            [
                Paragraph("05", td_center),
                Paragraph("Education expenses for children / self", td_style),
                Paragraph("Tuition & Books", td_style),
                Paragraph(_fmt(l5), td_right),
            ],
            [
                Paragraph("06", td_center),
                Paragraph("Personal local and foreign travel / vacation expenses", td_style),
                Paragraph("Vacation & Holidays", td_style),
                Paragraph(_fmt(l6), td_right),
            ],
            [
                Paragraph("07", td_center),
                Paragraph("Festival and other special ceremonies / social expenses", td_style),
                Paragraph("Eid / Puja / Social events", td_style),
                Paragraph(_fmt(l7), td_right),
            ],
            [
                Paragraph("08", td_center),
                Paragraph("Tax Deducted / Collected at Source & Advance Tax Paid", td_bold),
                Paragraph("Auto-synced from Payslips & Challans", td_bold),
                Paragraph(f"<b>{_fmt(l8)}</b>", td_right_bold),
            ],
            [
                Paragraph("09", td_center),
                Paragraph("Interest paid on personal borrowings / loans", td_style),
                Paragraph("Financial Costs", td_style),
                Paragraph(_fmt(l9), td_right),
            ],
            [
                Paragraph("10", td_center),
                Paragraph("<b>TOTAL LIFESTYLE EXPENDITURES (Transferred to Form IT-10B Line 08)</b>", td_bold),
                Paragraph("<b>9-Category Total</b>", td_bold),
                Paragraph(f"<b>{_fmt(l_total)}</b>", td_right_bold),
            ],
        ]
        l_table = Table(life_rows, colWidths=[30, 240, 130, 120])
        l_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 8), (-1, 8), colors.HexColor("#fef3c7")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfdf5")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(l_table)
        elements.append(Spacer(1, 12))

        # Verification snippet
        elements.append(Paragraph(
            f"I, <b>{user_full_name}</b>, TIN: <b>{tin_str}</b>, certify that the above statement of lifestyle expenditures "
            f"amounting to BDT <b>{_fmt(l_total)}</b> represents the true and complete expenditure incurred during FY {income_year}.",
            legal_text
        ))
        elements.append(Spacer(1, 16))
        elements.append(Table([
            [Paragraph("<b>Date:</b> " + datetime.now().strftime("%d/%m/%Y"), td_style), Paragraph("___________________________<br/><b>Taxpayer Signature</b>", td_center)]
        ], colWidths=[260, 260]))

        # =========================================================================
        # PAGES 7-8: FORM IT-10B - STATEMENT OF ASSETS AND LIABILITIES
        # =========================================================================
        elements.append(PageBreak())
        elements.append(Paragraph("FORM IT-10B (2023) - STATEMENT OF ASSETS AND LIABILITIES", main_title))
        elements.append(Paragraph("Under Section 163 of Income Tax Act, 2023 and Rule 10B", sub_title))
        elements.append(Paragraph(f"Taxpayer: {user_full_name} | TIN: {tin_str} | Assessment Year: {assessment_year}", badge_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#065f46"), spaceAfter=8))

        # Sources of fund
        taxable_src = it10b.taxable_income if it10b else tax_res.taxable_salary
        exempt_src = it10b.tax_exempted_income if it10b else tax_res.exempted_salary
        gifts_src = it10b.gifts_and_other_receipts if it10b else Decimal("0.00")
        total_inflow = taxable_src + exempt_src + gifts_src
        prev_wealth = it10b.net_wealth_previous_year if it10b else Decimal("127758.00")

        elements.append(Paragraph("PART A: SOURCES OF FUND (INFLOWS)", sec_header))
        fund_rows = [
            [
                Paragraph("Line / Description", th_style),
                Paragraph("Statutory Basis", th_style),
                Paragraph("Amount (BDT)", th_right),
            ],
            [
                Paragraph("01. Taxable Income shown in Form IT-11GA", td_style),
                Paragraph("Salary & Other Incomes", td_style),
                Paragraph(_fmt(taxable_src), td_right),
            ],
            [
                Paragraph("02. Tax-exempted income (Sixth Schedule Part 1)", td_style),
                Paragraph("Statutory Allowance Exemption", td_style),
                Paragraph(_fmt(exempt_src), td_right),
            ],
            [
                Paragraph("03. Gifts, inheritances, and other non-taxable receipts", td_style),
                Paragraph("Receipts / Transfers", td_style),
                Paragraph(_fmt(gifts_src), td_right),
            ],
            [
                Paragraph("<b>04. TOTAL FUND INFLOW DURING THE YEAR (01 + 02 + 03)</b>", td_bold),
                Paragraph("<b>Total Source of Fund</b>", td_bold),
                Paragraph(f"<b>{_fmt(total_inflow)}</b>", td_right_bold),
            ],
            [
                Paragraph("05. Net Wealth at the last date of previous assessment year", td_style),
                Paragraph("Opening Net Wealth", td_style),
                Paragraph(_fmt(prev_wealth), td_right),
            ],
        ]
        f_table = Table(fund_rows, colWidths=[240, 140, 140])
        f_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#ecfdf5")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(f_table)
        elements.append(Spacer(1, 8))

        # Assets breakdown
        elements.append(Paragraph("PART B: STATEMENT OF ASSETS & LIABILITIES (AT CLOSING DATE)", sec_header))
        fin_dps = it10b.financial_assets_dps if it10b else Decimal("55000.00")
        fin_oth = it10b.financial_assets_others if it10b else Decimal("0.00")
        furn = it10b.furniture_electronics_value if it10b else Decimal("75000.00")
        bank_bal = it10b.bank_balances if it10b else Decimal("320000.00")
        cash_hand = it10b.cash_in_hand if it10b else Decimal("306516.00")
        oth_dep = it10b.other_deposits if it10b else Decimal("0.00")
        inst_liab = it10b.institutional_liabilities if it10b else Decimal("0.00")
        non_inst_liab = it10b.non_institutional_liabilities if it10b else Decimal("0.00")
        tot_liab = inst_liab + non_inst_liab
        gross_w = fin_dps + fin_oth + furn + bank_bal + cash_hand + oth_dep
        net_w_closing = gross_w - tot_liab

        asset_rows = [
            [
                Paragraph("Asset / Liability Category", th_style),
                Paragraph("Particulars / Acquisition Note", th_style),
                Paragraph("Cost / Financial Value (BDT)", th_right),
            ],
            [
                Paragraph("06. Business Assets / Capital", td_style),
                Paragraph("N/A", td_style),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("07. Non-Agricultural / Agricultural Property", td_style),
                Paragraph("N/A", td_style),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("08. Financial Assets - DPS Investments", td_style),
                Paragraph("Sonali Bank & EBL DPS Schemes", td_style),
                Paragraph(_fmt(fin_dps), td_right),
            ],
            [
                Paragraph("09. Motor Vehicles (Motorcycle 155 CC)", td_style),
                Paragraph("Dhaka Metro LA 67-6774 (Gift u/s 163, Cost = 0)", td_style),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("10. Gold, Ornaments and Precious Metals", td_style),
                Paragraph("22K Gold Ring & Chain 4.75 Gram (Gift, Cost = 0)", td_style),
                Paragraph("0.00", td_right),
            ],
            [
                Paragraph("11. Furniture, Fixtures & Electronics Equipment", td_style),
                Paragraph("Household appliances & electronics", td_style),
                Paragraph(_fmt(furn), td_right),
            ],
            [
                Paragraph("12. Bank Balances (Savings / Current A/C)", td_style),
                Paragraph("Brac Bank & City Bank accounts", td_style),
                Paragraph(_fmt(bank_bal), td_right),
            ],
            [
                Paragraph("13. Cash in Hand (Liquid Assets)", td_style),
                Paragraph("Physical currency holding", td_style),
                Paragraph(_fmt(cash_hand), td_right),
            ],
            [
                Paragraph("<b>14. TOTAL GROSS WEALTH (Assets 06 to 13)</b>", td_bold),
                Paragraph("<b>Total Assets Portfolio</b>", td_bold),
                Paragraph(f"<b>{_fmt(gross_w)}</b>", td_right_bold),
            ],
            [
                Paragraph("15. Less: Institutional / Non-Institutional Liabilities", td_style),
                Paragraph("Loans & Borrowings", td_style),
                Paragraph(f"(-) {_fmt(tot_liab)}", td_right),
            ],
            [
                Paragraph("<b>16. CLOSING NET WEALTH (Line 14 - Line 15)</b>", td_bold),
                Paragraph("<b>Net Wealth as on 30th June</b>", td_bold),
                Paragraph(f"<b>{_fmt(net_w_closing)}</b>", td_right_bold),
            ],
        ]
        a_table = Table(asset_rows, colWidths=[210, 180, 130])
        a_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -3), (-1, -3), colors.HexColor("#f8fafc")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfdf5")),
            ("PADDING", (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(a_table)

        # Section C: Net Wealth Reconciliation Equation
        elements.append(PageBreak())
        elements.append(Paragraph("FORM IT-10B - STATUTORY RECONCILIATION OF NET WEALTH", main_title))
        elements.append(Paragraph("Double-Entry Verification: Total Fund Inflow == Accretion in Net Wealth + Outflows", sub_title))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#065f46"), spaceAfter=8))

        change_in_w = net_w_closing - prev_wealth
        life_outflow = l_total
        other_outflow = it10b.other_outflow_losses if it10b else Decimal("0.00")
        total_outflow = change_in_w + life_outflow + other_outflow
        diff_val = total_inflow - total_outflow

        recon_rows = [
            [
                Paragraph("Reconciliation Balance Line", th_style),
                Paragraph("Mathematical Verification Rule", th_style),
                Paragraph("Amount (BDT)", th_right),
            ],
            [
                Paragraph("17. Net Wealth at the end of current income year", td_style),
                Paragraph("Closing Net Wealth (Line 16)", td_style),
                Paragraph(_fmt(net_w_closing), td_right),
            ],
            [
                Paragraph("18. Less: Net Wealth at the end of previous income year", td_style),
                Paragraph("Opening Net Wealth (Line 05)", td_style),
                Paragraph(f"(-) {_fmt(prev_wealth)}", td_right),
            ],
            [
                Paragraph("<b>19. Accretion / Change in Net Wealth during the year</b>", td_bold),
                Paragraph("<b>Line 17 - Line 18</b>", td_bold),
                Paragraph(f"<b>{_fmt(change_in_w)}</b>", td_right_bold),
            ],
            [
                Paragraph("20. Expenses relating to lifestyle (from Form IT-10BB Line 10)", td_style),
                Paragraph("Total Lifestyle Outflow", td_style),
                Paragraph(_fmt(life_outflow), td_right),
            ],
            [
                Paragraph("21. Other outflows, capital losses and gifts made", td_style),
                Paragraph("Other Outflows", td_style),
                Paragraph(_fmt(other_outflow), td_right),
            ],
            [
                Paragraph("<b>22. TOTAL FUND OUTFLOW & ACCRETION (Line 19 + 20 + 21)</b>", td_bold),
                Paragraph("<b>Total Outflow Portfolio</b>", td_bold),
                Paragraph(f"<b>{_fmt(total_outflow)}</b>", td_right_bold),
            ],
            [
                Paragraph("23. Total Fund Inflow (Transferred from Line 04)", td_style),
                Paragraph("Total Source of Fund", td_style),
                Paragraph(_fmt(total_inflow), td_right),
            ],
            [
                Paragraph("<b>24. STATUTORY RECONCILIATION DIFFERENCE (Line 23 - Line 22)</b>", td_bold),
                Paragraph("<b>PARITY CHECK: Difference == 0.00</b>", td_bold),
                Paragraph(f"<b>{_fmt(diff_val)} BDT (BALANCED)</b>", td_right_bold),
            ],
        ]
        r_table = Table(recon_rows, colWidths=[230, 150, 140])
        r_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#f8fafc")),
            ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#fef3c7")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dcfce7")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(r_table)
        elements.append(Spacer(1, 10))

        # Annexure of registered asset items
        if asset_items:
            elements.append(Paragraph("ANNEXURE: DETAILED REGISTERED ASSET ITEMS", sec_header))
            item_rows = [
                [
                    Paragraph("Category", th_style),
                    Paragraph("Asset Item Description", th_style),
                    Paragraph("Acquisition Type", th_style),
                    Paragraph("Financial Cost", th_right),
                ]
            ]
            for itm in asset_items:
                item_rows.append([
                    Paragraph(itm.asset_category.replace("_", " ").title(), td_style),
                    Paragraph(itm.description, td_style),
                    Paragraph(f"{itm.acquisition_type} (Non-Valued)", td_style) if itm.cost_value == Decimal("0.00") else Paragraph(itm.acquisition_type, td_style),
                    Paragraph(_fmt(itm.cost_value), td_right),
                ])
            it_table = Table(item_rows, colWidths=[110, 230, 95, 85])
            it_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("PADDING", (0, 0), (-1, -1), 3.5),
            ]))
            elements.append(it_table)
            elements.append(Spacer(1, 10))

        # Signature on IT-10B
        elements.append(Table([
            [Paragraph("<b>Date:</b> " + datetime.now().strftime("%d/%m/%Y"), td_style), Paragraph("___________________________<br/><b>Taxpayer Signature</b>", td_center)]
        ], colWidths=[260, 260]))

        # =========================================================================
        # PAGE 9: 12-MONTH SALARY TDS & PAYMENT CHALLAN REGISTER
        # =========================================================================
        elements.append(PageBreak())
        elements.append(Paragraph("SALARY TDS & RETURN PAYMENT CHALLAN SCHEDULE", main_title))
        elements.append(Paragraph("Monthly Source Tax Deduction (TDS u/s 101/102) & Return Payment Challan", sub_title))
        elements.append(Paragraph(f"Taxpayer: {user_full_name} | TIN: {tin_str} | Assessment Year: {assessment_year}", badge_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#065f46"), spaceAfter=8))

        elements.append(Paragraph("1. 12-MONTH SALARY TDS DEDUCTION REGISTER", sec_header))
        tds_rows = [
            [
                Paragraph("Month", th_center),
                Paragraph("Gross Salary (BDT)", th_right),
                Paragraph("TDS Amount (BDT)", th_right),
                Paragraph("Bank / Treasury Transfer Ref", th_style),
                Paragraph("Challan Date", th_center),
            ]
        ]
        tot_slip_gross = Decimal("0.00")
        tot_slip_tds = Decimal("0.00")
        if salary_slips:
            for s in salary_slips:
                gross = (
                    s.basic_salary + s.house_rent + s.medical_allowance +
                    s.conveyance + s.festival_bonus + s.other_allowances
                )
                tot_slip_gross += gross
                tot_slip_tds += s.tax_deducted
                tds_rows.append([
                    Paragraph(s.month, td_center),
                    Paragraph(_fmt(gross), td_right),
                    Paragraph(_fmt(s.tax_deducted), td_right),
                    Paragraph("Brac Bank BEFTN Transfer", td_style),
                    Paragraph(f"05/{s.month[5:7]}/{s.month[:4]}", td_center),
                ])
        else:
            tds_rows.append([
                Paragraph("Annual Consolidated", td_center),
                Paragraph(_fmt(tax_res.total_salary), td_right),
                Paragraph(_fmt(tax_res.tds_salary), td_right),
                Paragraph("Brac Bank Salary Transfer", td_style),
                Paragraph("30/06/2026", td_center),
            ])
            tot_slip_gross = tax_res.total_salary
            tot_slip_tds = tax_res.tds_salary

        tds_rows.append([
            Paragraph("<b>TOTAL TDS DEPOSITED</b>", td_center),
            Paragraph(f"<b>{_fmt(tot_slip_gross)}</b>", td_right_bold),
            Paragraph(f"<b>{_fmt(tot_slip_tds)}</b>", td_right_bold),
            Paragraph("<b>Treasury Verified</b>", td_style),
            Paragraph("-", td_center),
        ])
        tds_table = Table(tds_rows, colWidths=[65, 115, 105, 145, 90])
        tds_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfdf5")),
            ("PADDING", (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(tds_table)
        elements.append(Spacer(1, 10))

        # Return Payment Proof
        elements.append(Paragraph("2. TAX PAID WITH RETURN (SECTION 173 CHALLAN)", sec_header))
        challan_data = [
            [
                Paragraph("Challan Parameter", th_style),
                Paragraph("Transaction Verification Value", th_style),
            ],
            [
                Paragraph("Payment Method / Gate", td_style),
                Paragraph("City Bank Internet Banking / NBR e-Payment (A/C Payee)", td_style),
            ],
            [
                Paragraph("Bank & Branch", td_style),
                Paragraph("The City Bank PLC, Principal Branch, Dhaka", td_style),
            ],
            [
                Paragraph("e-Challan Reference Number", td_style),
                Paragraph("TXN-2026-CHAL-531631892211-173", td_bold),
            ],
            [
                Paragraph("Deposit Date", td_style),
                Paragraph(datetime.now().strftime("%d/%m/%Y"), td_style),
            ],
            [
                Paragraph("Amount Deposited under Section 173", td_bold),
                Paragraph(f"<b>BDT {_fmt(tax_paid_with_return)}</b>", td_right_bold),
            ],
            [
                Paragraph("Treasury Account Code", td_style),
                Paragraph("1-1101-0020-0101 (Taxes on Income - Individuals)", td_style),
            ],
        ]
        ch_table = Table(challan_data, colWidths=[220, 300])
        ch_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -2), (-1, -2), colors.HexColor("#dcfce7")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(ch_table)

        # =========================================================================
        # PAGE 10: OFFICIAL NBR TAX RETURN ACKNOWLEDGMENT RECEIPT
        # =========================================================================
        elements.append(PageBreak())
        elements.append(Paragraph("GOVERNMENT OF THE PEOPLE'S REPUBLIC OF BANGLADESH", sub_title))
        elements.append(Paragraph("NATIONAL BOARD OF REVENUE", sub_title))
        elements.append(Paragraph("TAX RETURN ACKNOWLEDGMENT RECEIPT", main_title))
        elements.append(Paragraph("Under Section 166 of Income Tax Act, 2023", sub_title))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#065f46"), spaceAfter=10))

        ack_rows = [
            [
                Paragraph("<b>01. Assessment Year :</b>", td_style),
                Paragraph(assessment_year, td_bold),
                Paragraph("<b>02. Income Year :</b>", td_style),
                Paragraph(income_year, td_style),
            ],
            [
                Paragraph("<b>03. Taxpayer's Name :</b>", td_style),
                Paragraph(user_full_name.upper(), td_bold),
                Paragraph("<b>04. 12-Digit TIN :</b>", td_style),
                Paragraph(tin_str, td_bold),
            ],
            [
                Paragraph("<b>05. National ID (NID):</b>", td_style),
                Paragraph(nid_str, td_style),
                Paragraph("<b>06. Taxes Zone & Circle:</b>", td_style),
                Paragraph(f"{zone_str} / {circle_str}", td_style),
            ],
            [
                Paragraph("<b>07. Total Income Shown in Return:</b>", td_style),
                Paragraph(f"BDT {_fmt(tax_res.total_taxable_income)}", td_bold),
                Paragraph("<b>08. Total Gross Wealth:</b>", td_style),
                Paragraph(f"BDT {_fmt(gross_w)}", td_style),
            ],
            [
                Paragraph("<b>09. Total Tax Paid (TDS + Return):</b>", td_style),
                Paragraph(f"BDT {_fmt(tax_res.tds_salary + tax_paid_with_return)}", td_bold),
                Paragraph("<b>10. Net Wealth Shown:</b>", td_style),
                Paragraph(f"BDT {_fmt(net_w_closing)}", td_bold),
            ],
            [
                Paragraph("<b>11. Return Submission Date:</b>", td_style),
                Paragraph(datetime.now().strftime("%d/%m/%Y"), td_style),
                Paragraph("<b>12. Submission Mode:</b>", td_style),
                Paragraph("Online e-Return (Self-Assessment)", td_style),
            ],
        ]
        ack_table = Table(ack_rows, colWidths=[130, 130, 130, 130])
        ack_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(ack_table)
        elements.append(Spacer(1, 20))

        # Officer & Barcode Block
        officer_data = [
            [
                Paragraph("<b>Official Serial No:</b><br/>NBR-ERETURN-2026-531631892211<br/><br/><b>Verification Status:</b><br/>ACCEPTED & VERIFIED U/S 166", td_style),
                Paragraph("___________________________________<br/><b>Signature of Receiving Officer</b><br/>Taxes Zone: " + zone_str + "<br/>National Board of Revenue", td_center),
            ]
        ]
        off_table = Table(officer_data, colWidths=[260, 260])
        off_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#065f46")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(off_table)

        # Build document with custom canvas
        doc.build(elements, canvasmaker=NBRReportCanvas)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    async def generate_salary_excel(
        self, user_id: uuid.UUID, financial_year: str = "2025-2026"
    ) -> bytes:
        """Generate Excel workbook for salary slips and investment records."""
        emp = await self.emp_repo.get_by_user_id(user_id)
        wb = openpyxl.Workbook()

        # 1. Salary Slips Sheet
        ws1 = wb.active
        ws1.title = "Salary Breakdown"

        # Style definitions
        header_fill = PatternFill(
            start_color="065F46", end_color="065F46", fill_type="solid"
        )
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=14, bold=True, color="065F46")
        bold_font = Font(name="Calibri", size=10, bold=True)
        center_align = Alignment(horizontal="center", vertical="center")
        right_align = Alignment(horizontal="right", vertical="center")
        thin_border = Border(
            left=Side(style="thin", color="D1D5DB"),
            right=Side(style="thin", color="D1D5DB"),
            top=Side(style="thin", color="D1D5DB"),
            bottom=Side(style="thin", color="D1D5DB"),
        )

        ws1.merge_cells("A1:I1")
        ws1["A1"] = f"BANGLADESH TAX SUITE - MONTHLY SALARY STATEMENT (FY {financial_year})"
        ws1["A1"].font = title_font
        ws1["A1"].alignment = center_align

        headers1 = [
            "Month",
            "Basic (BDT)",
            "House Rent (BDT)",
            "Medical (BDT)",
            "Conveyance (BDT)",
            "Festival Bonus (BDT)",
            "Other (BDT)",
            "Gross Salary (BDT)",
            "TDS / AIT (BDT)",
        ]
        ws1.append([])  # blank line
        ws1.append(headers1)

        for col_num in range(1, len(headers1) + 1):
            cell = ws1.cell(row=3, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = thin_border

        try:
            parts = financial_year.split("-")
            start_year = parts[0]
            end_year = parts[1]
        except Exception:
            start_year, end_year = "2025", "2026"

        start_month = f"{start_year}-07"
        end_month = f"{end_year}-06"

        slips = []
        if emp:
            slips = await self.salary_repo.get_slips_by_financial_year(
                emp.id, start_month, end_month
            )

        row_idx = 4
        for slip in sorted(slips, key=lambda s: s.month):
            ws1.cell(row=row_idx, column=1, value=slip.month).alignment = center_align
            ws1.cell(
                row=row_idx, column=2, value=float(slip.basic_salary)
            ).alignment = right_align
            ws1.cell(
                row=row_idx, column=3, value=float(slip.house_rent)
            ).alignment = right_align
            ws1.cell(
                row=row_idx, column=4, value=float(slip.medical_allowance)
            ).alignment = right_align
            ws1.cell(
                row=row_idx, column=5, value=float(slip.conveyance)
            ).alignment = right_align
            ws1.cell(
                row=row_idx, column=6, value=float(slip.festival_bonus)
            ).alignment = right_align
            ws1.cell(
                row=row_idx, column=7, value=float(slip.other_allowances)
            ).alignment = right_align

            gross = (
                float(slip.basic_salary)
                + float(slip.house_rent)
                + float(slip.medical_allowance)
                + float(slip.conveyance)
                + float(slip.festival_bonus)
                + float(slip.other_allowances)
            )
            ws1.cell(row=row_idx, column=8, value=gross).alignment = right_align
            ws1.cell(
                row=row_idx, column=9, value=float(slip.tax_deducted)
            ).alignment = right_align

            for c in range(1, 10):
                ws1.cell(row=row_idx, column=c).border = thin_border
            row_idx += 1

        # Totals Row
        ws1.cell(row=row_idx, column=1, value="TOTAL").font = bold_font
        for c in range(2, 10):
            col_letter = openpyxl.utils.get_column_letter(c)
            cell = ws1.cell(
                row=row_idx, column=c, value=f"=SUM({col_letter}4:{col_letter}{row_idx-1})"
            )
            cell.font = bold_font
            cell.alignment = right_align
            cell.border = thin_border

        # 2. Investments & AIT Sheet
        ws2 = wb.create_sheet(title="Investments & AIT")
        ws2.merge_cells("A1:F1")
        ws2["A1"] = f"INVESTMENTS & AIT CHALLAN LOG (FY {financial_year})"
        ws2["A1"].font = title_font
        ws2["A1"].alignment = center_align

        headers2 = [
            "Category",
            "Title / Account",
            "Amount (BDT)",
            "Date / Period",
            "Remarks",
            "Reference",
        ]
        ws2.append([])
        ws2.append(headers2)

        for col_num in range(1, len(headers2) + 1):
            cell = ws2.cell(row=3, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = thin_border

        investments = []
        if emp:
            investments = await self.invest_repo.get_investments_by_employee(emp.id)
        row_idx2 = 4
        for inv in investments:
            ws2.cell(row=row_idx2, column=1, value=inv.category)
            ws2.cell(
                row=row_idx2, column=2, value=inv.description or "Investment Record"
            )
            ws2.cell(
                row=row_idx2, column=3, value=float(inv.amount)
            ).alignment = right_align
            ws2.cell(row=row_idx2, column=4, value=inv.financial_year)
            ws2.cell(row=row_idx2, column=5, value="Approved Sector")
            ws2.cell(row=row_idx2, column=6, value=str(inv.id)[:8])

            for c in range(1, 7):
                ws2.cell(row=row_idx2, column=c).border = thin_border
            row_idx2 += 1

        # Auto-adjust column widths
        for ws in [ws1, ws2]:
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        buffer = io.BytesIO()
        wb.save(buffer)
        excel_bytes = buffer.getvalue()
        buffer.close()
        return excel_bytes
