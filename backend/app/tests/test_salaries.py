import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_salary_slip_workflow(client: AsyncClient):
    # 1. Register and login a standard user
    register_payload = {
        "email": "salary.user@example.com",
        "phone": "+8801722222222",
        "first_name": "Salary",
        "last_name": "Tester",
        "password": "strongpassword"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_res = await client.post("/api/v1/auth/login", json={
        "username": "salary.user@example.com",
        "password": "strongpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Try to add slip before setting up employee profile -> Should return 400
    slip_payload = {
        "month": "2025-07",
        "basic_salary": "50000.00",
        "house_rent": "25000.00",
        "medical_allowance": "5000.00",
        "conveyance": "2500.00",
        "festival_bonus": "0.00",
        "provident_fund": "5000.00",
        "employer_provident_fund": "5000.00",
        "other_allowances": "1000.00",
        "tax_deducted": "2000.00"
    }
    res = await client.post("/api/v1/salaries/slips", json=slip_payload, headers=headers)
    assert res.status_code == 400
    assert "Employee profile not setup" in res.json()["detail"]

    # 3. Setup employee profile
    profile_payload = {
        "designation": "Staff QA",
        "department": "Engineering",
        "date_of_joining": "2024-06-01",
        "nid": "9876543210",
        "tax_zone": "Zone 5, Dhaka",
        "tax_circle": "Circle 90"
    }
    await client.post("/api/v1/employees/profile", json=profile_payload, headers=headers)

    # 4. Now add slip -> Should succeed with 201
    res = await client.post("/api/v1/salaries/slips", json=slip_payload, headers=headers)
    assert res.status_code == 201
    assert res.json()["month"] == "2025-07"
    assert float(res.json()["basic_salary"]) == 50000.0

    # 5. Add second month slip
    slip_payload_aug = {**slip_payload, "month": "2025-08", "festival_bonus": "50000.00"}
    res = await client.post("/api/v1/salaries/slips", json=slip_payload_aug, headers=headers)
    assert res.status_code == 201

    # 6. Retrieve list of slips -> Should contain 2 slips
    res = await client.get("/api/v1/salaries/slips", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2

    # 7. Get financial year summary -> Should aggregate components
    res = await client.get("/api/v1/salaries/summary?financial_year=2025-2026", headers=headers)
    assert res.status_code == 200
    summary = res.json()
    assert summary["months_count"] == 2
    assert float(summary["total_basic"]) == 100000.0
    assert float(summary["total_bonus"]) == 50000.0
    assert float(summary["gross_salary"]) == (100000.0 + 50000.0 + 10000.0 + 5000.0 + 50000.0 + 2000.0)

    # 8. Delete a slip
    slips_list = (await client.get("/api/v1/salaries/slips", headers=headers)).json()
    slip_id = slips_list[0]["id"]
    res = await client.delete(f"/api/v1/salaries/slips/{slip_id}", headers=headers)
    assert res.status_code == 204

    # 9. Verify list of slips now has only 1 slip
    res = await client.get("/api/v1/salaries/slips", headers=headers)
    assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_salary_certificate_upload_and_adjust(client: AsyncClient):
    # Setup employee profile
    register_payload = {
        "email": "cert.user@example.com",
        "phone": "+8801733333333",
        "first_name": "Cert",
        "last_name": "Tester",
        "password": "strongpassword"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_res = await client.post("/api/v1/auth/login", json={
        "username": "cert.user@example.com",
        "password": "strongpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_payload = {
        "designation": "Manager",
        "nid": "1122334455"
    }
    await client.post("/api/v1/employees/profile", json=profile_payload, headers=headers)

    # Multipart/form-data file upload
    file_data = BytesIO(b"%PDF-1.4 dummy pdf content")
    files = {"file": ("salary_certificate.pdf", file_data, "application/pdf")}
    data = {"financial_year": "2025-2026"}

    res = await client.post(
        "/api/v1/salaries/upload-certificate",
        data=data,
        files=files,
        headers=headers
    )
    assert res.status_code == 201
    cert = res.json()
    assert cert["file_name"] == "salary_certificate.pdf"
    assert cert["status"] == "Verified"
    assert float(cert["total_basic"]) == 600000.0
    
    cert_id = cert["id"]

    # Update certificate totals
    updates = {
        "total_basic": 620000.00,
        "total_house_rent": 310000.00
    }
    res = await client.put(f"/api/v1/salaries/certificates/{cert_id}", json=updates, headers=headers)
    assert res.status_code == 200
    assert float(res.json()["total_basic"]) == 620000.0

    # Delete certificate
    res = await client.delete(f"/api/v1/salaries/certificates/{cert_id}", headers=headers)
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_salary_certificate_ocr_parsing(client: AsyncClient):
    # Setup employee profile
    register_payload = {
        "email": "ocr.user@example.com",
        "phone": "+8801733333334",
        "first_name": "OCR",
        "last_name": "Tester",
        "password": "strongpassword"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_res = await client.post("/api/v1/auth/login", json={
        "username": "ocr.user@example.com",
        "password": "strongpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_payload = {
        "designation": "Staff",
        "nid": "1122334455"
    }
    await client.post("/api/v1/employees/profile", json=profile_payload, headers=headers)

    # Mock PdfReader
    mock_page = MagicMock()
    mock_page.extract_text.return_value = """
    OFFICIAL SALARY SUMMARY
    Basic Salary: 720,000.00
    House Rent: 360,000.00
    Medical Allowance: 144,000.00
    Conveyance Allowance: 36,000.00
    Festival Bonus: 120,000.00
    Provident Fund: 72,000.00
    Tax Deducted at Source (TDS): 30,000.00
    Other Allowance: 48,000.00
    """
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("pypdf.PdfReader", return_value=mock_reader):
        file_data = BytesIO(b"%PDF-1.4 mock pdf content")
        files = {"file": ("salary_certificate.pdf", file_data, "application/pdf")}
        data = {"financial_year": "2025-2026"}

        res = await client.post(
            "/api/v1/salaries/upload-certificate",
            data=data,
            files=files,
            headers=headers
        )
        assert res.status_code == 201
        cert = res.json()
        assert cert["file_name"] == "salary_certificate.pdf"
        assert float(cert["total_basic"]) == 720000.0
        assert float(cert["total_house_rent"]) == 360000.0
        assert float(cert["total_medical"]) == 144000.0
        assert float(cert["total_conveyance"]) == 36000.0
        assert float(cert["total_bonus"]) == 120000.0
        assert float(cert["total_provident_fund"]) == 72000.0
        assert float(cert["total_tax_deducted"]) == 30000.0
        assert float(cert["total_others"]) == 48000.0

