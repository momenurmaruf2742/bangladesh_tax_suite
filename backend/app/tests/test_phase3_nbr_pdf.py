import io
import pytest
from httpx import AsyncClient
import pypdf


@pytest.mark.asyncio
async def test_nbr_form_it11ga_multipage_pdf_generation(client: AsyncClient):
    """
    Test Phase 3: NBR Form IT-11GA (2023) Compliant Multi-Page PDF Generation.
    Verifies that the generated PDF contains authentic multi-page statutory sections:
    - Form IT-11GA (2023) Parts 1-5
    - Schedule 1 (Part b) - Employment Income
    - Schedule 5 - Investment Tax Rebate
    - Form IT-10BB - Statement of Lifestyle Expenses
    - Form IT-10B - Statement of Assets and Liabilities
    - TDS Challan Schedule & NBR Acknowledgment Receipt
    """
    # 1. Register & Login User
    reg_payload = {
        "email": "nbr_pdf_tester@taxsuite.com",
        "phone": "+8801999999999",
        "first_name": "Maruf",
        "last_name": "Chowdhury",
        "password": "strongpassword123",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json={
        "username": "nbr_pdf_tester@taxsuite.com",
        "password": "strongpassword123",
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup Employee Profile with Circle & Zone
    profile_payload = {
        "designation": "Principal Engineer",
        "department": "Core Platform",
        "nid": "1994123456789",
        "tax_zone": "Zone 15, Dhaka",
        "tax_circle": "Circle 330",
        "gender": "Male",
        "location": "Dhaka/Chittagong City Corporation",
    }
    await client.post("/api/v1/employees/profile", json=profile_payload, headers=headers)

    # 3. Create IT-10BB Lifestyle Expenses
    lifestyle_payload = {
        "financial_year": "2025-2026",
        "assessment_year": "2026-2027",
        "fooding_clothing_essentials": 150000.00,
        "housing_expense": 70000.00,
        "transport_expense": 50000.00,
        "utility_expense": 49000.00,
        "festival_special_expenses": 50000.00,
        "tax_deducted_source_advance": 9542.00,
    }
    await client.post("/api/v1/taxes/it10bb", json=lifestyle_payload, headers=headers)

    # 4. Create IT-10B Statement of Assets & Liabilities
    it10b_payload = {
        "financial_year": "2025-2026",
        "assessment_year": "2026-2027",
        "taxable_income": 671533.00,
        "tax_exempted_income": 335767.00,
        "net_wealth_previous_year": 127758.00,
        "lifestyle_expenses": 378542.00,
        "financial_assets_dps": 55000.00,
        "furniture_electronics_value": 75000.00,
        "bank_balances": 320000.00,
        "cash_in_hand": 306516.00,
    }
    stmt_res = await client.post("/api/v1/taxes/it10b", json=it10b_payload, headers=headers)
    stmt_id = stmt_res.json()["id"]

    # 5. Add Non-Valued Gift Asset (Motor Vehicle & Gold)
    asset_payload = {
        "asset_category": "motor_vehicles",
        "description": "Dhaka Metro LA 67-6774 Suzuki Gixxer (155 CC)",
        "acquisition_type": "Gift",
        "cost_value": 0.00,
        "particulars": {"engine_cc": "155 CC", "status": "Gift"},
    }
    await client.post(f"/api/v1/taxes/it10b/{stmt_id}/assets", json=asset_payload, headers=headers)

    # 6. Request Official Multi-Page NBR Form IT-11GA PDF
    pdf_res = await client.get("/api/v1/reports/tax-return/pdf?financial_year=2025-2026", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 10000

    # 7. Parse & Inspect PDF Structure
    reader = pypdf.PdfReader(io.BytesIO(pdf_res.content))
    assert len(reader.pages) >= 8

    full_pdf_text = "".join(page.extract_text() for page in reader.pages)
    assert "FORM IT-11GA (2023)" in full_pdf_text
    assert "SCHEDULE 1 (Part b)" in full_pdf_text
    assert "SCHEDULE 5 - INVESTMENT TAX REBATE" in full_pdf_text
    assert "FORM IT-10BB (2023)" in full_pdf_text
    assert "FORM IT-10B (2023)" in full_pdf_text
    assert "TAX RETURN ACKNOWLEDGMENT RECEIPT" in full_pdf_text
    assert "Difference == 0.00" in full_pdf_text or "BALANCED" in full_pdf_text
