import io
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.users.repository import UserRepository
from app.modules.employees.repository import EmployeeRepository
from app.modules.salaries.repository import SalaryRepository
from app.modules.investments.repository import InvestmentRepository
from app.modules.taxes.service import TaxService


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.emp_repo = EmployeeRepository(db)
        self.salary_repo = SalaryRepository(db)
        self.invest_repo = InvestmentRepository(db)
        self.tax_service = TaxService(db)

    async def generate_tax_return_pdf(self, user_id: uuid.UUID, financial_year: str = "2025-2026") -> bytes:
        """Generate PDF Tax Return Summary & Computation Sheet according to Income Tax Act 2023."""
        user = await self.user_repo.get_by_id(user_id)
        emp = await self.emp_repo.get_by_user_id(user_id)
        
        # Calculate tax summary using tax service
        tax_details = await self.tax_service.calculate_tax(
            user_id=user_id,
            financial_year=financial_year
        )
        tax_res = tax_details.summary

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor('#065f46'),
            alignment=1, # Center
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#4b5563'),
            alignment=1,
            spaceAfter=15
        )
        heading2_style = ParagraphStyle(
            'Heading2Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#1f2937'),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#374151')
        )

        elements = []

        # Header
        elements.append(Paragraph("BANGLADESH INCOME TAX RETURN COMPUTATION SHEET", title_style))
        elements.append(Paragraph(f"Under Income Tax Act 2023 • Assessment Year: 2026-2027 (FY {financial_year})", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#10b981'), spaceAfter=12))

        # Personal Info Table
        user_name = f"{user.first_name if user else 'Taxpayer'} {user.last_name if user else ''}".strip()
        info_data = [
            [Paragraph("<b>Taxpayer Name:</b>", body_style), Paragraph(user_name, body_style),
             Paragraph("<b>TIN:</b>", body_style), Paragraph(user.tin if user and user.tin else "N/A", body_style)],
            [Paragraph("<b>Phone:</b>", body_style), Paragraph(user.phone if user else "N/A", body_style),
             Paragraph("<b>Email:</b>", body_style), Paragraph(user.email if user else "N/A", body_style)],
            [Paragraph("<b>Designation:</b>", body_style), Paragraph(emp.designation if emp else "N/A", body_style),
             Paragraph("<b>Tax Zone / Circle:</b>", body_style), Paragraph(f"{emp.tax_zone or 'N/A'} / {emp.tax_circle or 'N/A'}" if emp else "N/A", body_style)]
        ]
        info_table = Table(info_data, colWidths=[110, 160, 110, 160])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9fafb')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f3f4f6')),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 12))

        # Income Summary Section
        elements.append(Paragraph("1. Income & Taxable Salary Calculation", heading2_style))
        income_data = [
            ["Particulars", "Amount (BDT)", "Exempted (BDT)", "Taxable Amount (BDT)"],
            ["Gross Annual Salary & Allowances", f"BDT {tax_res.total_salary:,.2f}", f"BDT {tax_res.exempted_salary:,.2f}", f"BDT {tax_res.taxable_salary:,.2f}"],
            ["Other Taxable Income", f"BDT {tax_res.other_income:,.2f}", "BDT 0.00", f"BDT {tax_res.other_income:,.2f}"],
            ["Total Taxable Income (A)", "-", "-", f"BDT {tax_res.total_taxable_income:,.2f}"]
        ]
        income_table = Table(income_data, colWidths=[200, 110, 110, 120])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#065f46')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ecfdf5')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ]))
        elements.append(income_table)
        elements.append(Spacer(1, 12))

        # Investment Rebate Section
        elements.append(Paragraph("2. Investment Tax Rebate (Section 78)", heading2_style))
        rebate_data = [
            ["Rebate Criteria", "Value / Cap (BDT)"],
            ["Total Eligible Investment Made", f"BDT {tax_res.total_invested:,.2f}"],
            ["Max Allowable Investment (20% of Taxable Income)", f"BDT {float(tax_res.total_taxable_income) * 0.2:,.2f}"],
            ["Max Absolute Cap (Section 78)", "BDT 10,00,000.00"],
            ["Approved Rebate (15% of lower cap)", f"BDT {tax_res.investment_rebate:,.2f}"]
        ]
        rebate_table = Table(rebate_data, colWidths=[330, 210])
        rebate_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#fef3c7')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        elements.append(rebate_table)
        elements.append(Spacer(1, 12))

        # Tax Liability Section
        elements.append(Paragraph("3. Tax Liability & Final Payable / Refund", heading2_style))
        tax_data = [
            ["Particulars", "Amount (BDT)"],
            ["Gross Tax (Before Rebate)", f"BDT {tax_res.gross_tax:,.2f}"],
            ["Less: Investment Rebate (Section 78)", f"(-) BDT {tax_res.investment_rebate:,.2f}"],
            ["Net Tax Payable (After Rebate)", f"BDT {tax_res.net_tax:,.2f}"],
            ["Minimum Tax Applicable", f"BDT {tax_res.minimum_tax:,.2f}"],
            ["Less: Advance Tax Paid / AIT TDS Deducted", f"(-) BDT {tax_res.ait_paid:,.2f}"],
            ["Final Net Tax Payable / (Refundable)", f"BDT {tax_res.final_payable:,.2f}"]
        ]
        tax_table = Table(tax_data, colWidths=[330, 210])
        tax_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#047857')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('PADDING', (0,0), (-1,-1), 5.5),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#dcfce7') if tax_res.final_payable <= 0 else colors.HexColor('#ffe4e6')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ]))
        elements.append(tax_table)
        elements.append(Spacer(1, 20))

        # Footer Signatures
        sig_data = [
            ["_________________________", "_________________________\nAuthorized NBR Representative"],
            [Paragraph(f"<b>Taxpayer Signature</b><br/>{user_name}", body_style), Paragraph("<b>Official Seal & Date</b>", body_style)]
        ]
        sig_table = Table(sig_data, colWidths=[270, 270])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(sig_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    async def generate_salary_excel(self, user_id: uuid.UUID, financial_year: str = "2025-2026") -> bytes:
        """Generate Excel workbook for salary slips and investment records."""
        emp = await self.emp_repo.get_by_user_id(user_id)
        wb = openpyxl.Workbook()
        
        # 1. Salary Slips Sheet
        ws1 = wb.active
        ws1.title = "Salary Breakdown"

        # Style definitions
        header_fill = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=14, bold=True, color="065F46")
        bold_font = Font(name="Calibri", size=10, bold=True)
        center_align = Alignment(horizontal="center", vertical="center")
        right_align = Alignment(horizontal="right", vertical="center")
        thin_border = Border(
            left=Side(style='thin', color='D1D5DB'),
            right=Side(style='thin', color='D1D5DB'),
            top=Side(style='thin', color='D1D5DB'),
            bottom=Side(style='thin', color='D1D5DB')
        )

        ws1.merge_cells("A1:I1")
        ws1["A1"] = f"BANGLADESH TAX SUITE - MONTHLY SALARY STATEMENT (FY {financial_year})"
        ws1["A1"].font = title_font
        ws1["A1"].alignment = center_align

        headers1 = ["Month", "Basic (BDT)", "House Rent (BDT)", "Medical (BDT)", "Conveyance (BDT)", "Festival Bonus (BDT)", "Other (BDT)", "Gross Salary (BDT)", "TDS / AIT (BDT)"]
        ws1.append([]) # blank line
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
            slips = await self.salary_repo.get_slips_by_financial_year(emp.id, start_month, end_month)
        
        row_idx = 4
        for slip in sorted(slips, key=lambda s: s.month):
            ws1.cell(row=row_idx, column=1, value=slip.month).alignment = center_align
            ws1.cell(row=row_idx, column=2, value=float(slip.basic_salary)).alignment = right_align
            ws1.cell(row=row_idx, column=3, value=float(slip.house_rent)).alignment = right_align
            ws1.cell(row=row_idx, column=4, value=float(slip.medical_allowance)).alignment = right_align
            ws1.cell(row=row_idx, column=5, value=float(slip.conveyance)).alignment = right_align
            ws1.cell(row=row_idx, column=6, value=float(slip.festival_bonus)).alignment = right_align
            ws1.cell(row=row_idx, column=7, value=float(slip.other_allowances)).alignment = right_align
            
            gross = (
                float(slip.basic_salary) + float(slip.house_rent) + float(slip.medical_allowance) +
                float(slip.conveyance) + float(slip.festival_bonus) + float(slip.other_allowances)
            )
            ws1.cell(row=row_idx, column=8, value=gross).alignment = right_align
            ws1.cell(row=row_idx, column=9, value=float(slip.tax_deducted)).alignment = right_align

            for c in range(1, 10):
                ws1.cell(row=row_idx, column=c).border = thin_border
            row_idx += 1

        # Totals Row
        ws1.cell(row=row_idx, column=1, value="TOTAL").font = bold_font
        for c in range(2, 10):
            col_letter = openpyxl.utils.get_column_letter(c)
            cell = ws1.cell(row=row_idx, column=c, value=f"=SUM({col_letter}4:{col_letter}{row_idx-1})")
            cell.font = bold_font
            cell.alignment = right_align
            cell.border = thin_border

        # 2. Investments & AIT Sheet
        ws2 = wb.create_sheet(title="Investments & AIT")
        ws2.merge_cells("A1:F1")
        ws2["A1"] = f"INVESTMENTS & AIT CHALLAN LOG (FY {financial_year})"
        ws2["A1"].font = title_font
        ws2["A1"].alignment = center_align

        headers2 = ["Category", "Title / Account", "Amount (BDT)", "Date / Period", "Remarks", "Reference"]
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
            ws2.cell(row=row_idx2, column=2, value=inv.description or "Investment Record")
            ws2.cell(row=row_idx2, column=3, value=float(inv.amount)).alignment = right_align
            ws2.cell(row=row_idx2, column=4, value=inv.financial_year)
            ws2.cell(row=row_idx2, column=5, value="Approved Sector")
            ws2.cell(row=row_idx2, column=6, value=str(inv.id)[:8])

            for c in range(1, 7):
                ws2.cell(row=row_idx2, column=c).border = thin_border
            row_idx2 += 1

        # Auto-adjust column widths
        for ws in [ws1, ws2]:
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        buffer = io.BytesIO()
        wb.save(buffer)
        excel_bytes = buffer.getvalue()
        buffer.close()
        return excel_bytes
