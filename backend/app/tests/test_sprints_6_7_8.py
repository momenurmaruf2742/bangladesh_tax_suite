import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sprints_6_7_8_features(client: AsyncClient):
    # 1. Register and login test user
    register_payload = {
        "email": "reports_ocr_ai_user@example.com",
        "phone": "+8801888888888",
        "first_name": "Report",
        "last_name": "Tester",
        "password": "strongpassword"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_res = await client.post("/api/v1/auth/login", json={
        "username": "reports_ocr_ai_user@example.com",
        "password": "strongpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup employee profile
    profile_payload = {
        "designation": "Tax Manager",
        "department": "Finance",
        "nid": "9876543210123",
        "gender": "Male",
        "location": "Dhaka/Chittagong City Corporation"
    }
    await client.post("/api/v1/employees/profile", json=profile_payload, headers=headers)

    # 3. Test Reports - PDF Tax Return Download
    res_pdf = await client.get("/api/v1/reports/tax-return/pdf?financial_year=2025-2026", headers=headers)
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 100

    # 4. Test Reports - Excel Salary Export Download
    res_excel = await client.get("/api/v1/reports/salary/excel?financial_year=2025-2026", headers=headers)
    assert res_excel.status_code == 200
    assert res_excel.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(res_excel.content) > 100

    # 5. Test AI Tax Assistant Chat API
    ai_req = {"prompt": "What is the maximum DPS investment rebate cap under Section 78?"}
    res_ai = await client.post("/api/v1/ai/tax-chat", json=ai_req, headers=headers)
    assert res_ai.status_code == 200
    ai_data = res_ai.json()
    assert "Section 78" in ai_data["reply"]
    assert len(ai_data["key_points"]) > 0

    # 6. Test OCR Document Parser endpoint with non-PDF error check
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    res_ocr_err = await client.post("/api/v1/ocr/parse-salary-pdf", files=files, headers=headers)
    assert res_ocr_err.status_code == 400
