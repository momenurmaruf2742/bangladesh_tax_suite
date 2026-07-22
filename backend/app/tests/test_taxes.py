import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tax_engine_workflow(client: AsyncClient):
    # 1. Register and login a standard user
    register_payload = {
        "email": "tax.user@example.com",
        "phone": "+8801744444444",
        "first_name": "Tax",
        "last_name": "Tester",
        "password": "strongpassword"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_res = await client.post("/api/v1/auth/login", json={
        "username": "tax.user@example.com",
        "password": "strongpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup employee profile (Female, Dhaka City Corporation)
    profile_payload = {
        "designation": "Staff Developer",
        "department": "Engineering",
        "nid": "112233445566",
        "gender": "Female",
        "location": "Dhaka/Chittagong City Corporation"
    }
    await client.post("/api/v1/employees/profile", json=profile_payload, headers=headers)

    # 3. Add monthly salary slips (e.g. 10 months of 60,000 BDT basic, 20,000 house rent, 10,000 other)
    # Total monthly = 90,000 BDT. Over 10 months = 900,000 BDT gross.
    # Tax deducted at source monthly = 2,000 BDT (Total TDS = 20,000 BDT)
    # Provident fund = 5,000 BDT, Employer PF = 5,000 BDT (Total PF = 100,000 BDT)
    for m in range(7, 12): # July to Nov (5 months)
        slip_payload = {
            "month": f"2025-{m:02d}",
            "basic_salary": "60000.00",
            "house_rent": "20000.00",
            "medical_allowance": "5000.00",
            "conveyance": "5000.00",
            "festival_bonus": "0.00",
            "provident_fund": "5000.00",
            "employer_provident_fund": "5000.00",
            "other_allowances": "10000.00",
            "tax_deducted": "2000.00"
        }
        res = await client.post("/api/v1/salaries/slips", json=slip_payload, headers=headers)
        assert res.status_code == 201

    # 4. Add eligible investments
    # DPS of 120,000 BDT (capping is checked in rebate limit)
    inv_payload = {
        "financial_year": "2025-2026",
        "category": "DPS",
        "amount": "120000.00",
        "description": "DPS log"
    }
    await client.post("/api/v1/investments", json=inv_payload, headers=headers)

    # 5. Add AIT paid logs
    # 15,000 BDT AIT
    ait_payload = {
        "financial_year": "2025-2026",
        "category": "Car Registration",
        "amount": "15000.00",
        "challan_number": "CH-12345",
        "description": "Car tax"
    }
    await client.post("/api/v1/investments/ait", json=ait_payload, headers=headers)

    # 6. Run Dynamic Tax Calculation endpoint
    # We have 5 months of slips:
    # Total monthly gross salary (including employer PF) = 60k + 20k + 5k + 5k + 10k + 5k = 105,000 BDT
    # Total salary (5 months) = 525,000 BDT.
    # Exemption = 1/3 of 525,000 = 175,000 BDT (since it's lower than 450,000 BDT).
    # Taxable salary = 525,000 - 175,000 = 350,000 BDT.
    # Total taxable income = 350,000 BDT.
    # Since user is Female, her tax-free limit is 400,000 BDT.
    # Because 350,000 <= 400,000, gross tax should be 0.0 BDT!
    calc_payload = {
        "financial_year": "2025-2026",
        "other_income": "0.00"
    }
    res = await client.post("/api/v1/taxes/calculate", json=calc_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert float(data["summary"]["total_salary"]) == 525000.0
    assert float(data["summary"]["exempted_salary"]) == 175000.0
    assert float(data["summary"]["taxable_salary"]) == 350000.0
    assert float(data["summary"]["gross_tax"]) == 0.0
    assert float(data["summary"]["net_tax"]) == 0.0

    # 7. Add other income to push taxable income above threshold
    # Add other income of 250,000 BDT.
    # Total taxable income = 350,000 + 250,000 = 600,000 BDT.
    # Slabs for Female (threshold 400,000 BDT):
    # - First 400,000 BDT: 0%
    # - Next 100,000 BDT: 5% (5,000 BDT tax)
    # - Next 100,000 BDT: 10% (10,000 BDT tax)
    # Gross tax should be 15,000 BDT!
    # Let's verify rebate:
    # PF (5 months) = 5k employee + 5k employer = 10k monthly = 50,000 BDT total PF.
    # Logged investments = 120,000 BDT.
    # Total invested = 170,000 BDT.
    # Eligible investment = min(170,000 BDT, 3% of 600,000 BDT = 18,000 BDT, 10 Lakhs BDT) = 18,000 BDT.
    # Investment rebate = 15% of 18,000 = 2,700 BDT.
    # Gross tax after rebate = 15,000 - 2,700 = 12,300 BDT.
    # Net tax (since 12,300 > minimum tax 5,000) = 12,300 BDT.
    # AIT adjustable: AIT paid = 15,000 BDT. TDS salary = 10,000 BDT. Total adjust = 25,000 BDT.
    # Final payable = 12,300 - 25,000 = -12,700 BDT (Refundable).
    calc_payload_other = {
        "financial_year": "2025-2026",
        "other_income": "250000.00"
    }
    res = await client.post("/api/v1/taxes/calculate", json=calc_payload_other, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert float(data["summary"]["total_taxable_income"]) == 600000.0
    assert float(data["summary"]["gross_tax"]) == 15000.0
    assert float(data["summary"]["eligible_investment"]) == 18000.0
    assert float(data["summary"]["investment_rebate"]) == 2700.0
    assert float(data["summary"]["minimum_tax"]) == 5000.0
    assert float(data["summary"]["net_tax"]) == 12300.0
    assert float(data["summary"]["ait_paid"]) == 15000.0
    assert float(data["summary"]["tds_salary"]) == 10000.0
    assert float(data["summary"]["final_payable"]) == -12700.0

    # 8. Calculate and Save calculation
    res = await client.post("/api/v1/taxes/calculate-save", json=calc_payload_other, headers=headers)
    assert res.status_code == 200
    save_data = res.json()
    calc_id = save_data["summary"]["id"]
    assert calc_id is not None

    # 9. Get calculation history
    res = await client.get("/api/v1/taxes/history", headers=headers)
    assert res.status_code == 200
    history = res.json()
    assert len(history) == 1
    # 9.5 Test NBR Return Form HTML Generation
    res = await client.get(f"/api/v1/taxes/history/{calc_id}/return/html", headers=headers)
    assert res.status_code == 200
    assert "IT-1152023" in res.text
    assert "National Board of Revenue" in res.text

    # 10. Delete calculation history record
    res = await client.delete(f"/api/v1/taxes/history/{calc_id}", headers=headers)
    assert res.status_code == 204

    # 11. Verify history is empty
    res = await client.get("/api/v1/taxes/history", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0
