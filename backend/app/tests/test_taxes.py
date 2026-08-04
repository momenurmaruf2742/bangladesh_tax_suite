import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tax_engine_workflow_2024_2025(client: AsyncClient):
    # 1. Register and login a standard user
    register_payload = {
        "email": "unique_tax_engine_user_2425@example.com",
        "phone": "+8801799999999",
        "first_name": "Tax",
        "last_name": "Tester",
        "password": "strongpassword",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "unique_tax_engine_user_2425@example.com",
            "password": "strongpassword",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup employee profile (Female, Dhaka City Corporation)
    profile_payload = {
        "designation": "Staff Developer",
        "department": "Engineering",
        "nid": "112233445566",
        "gender": "Female",
        "location": "Dhaka/Chittagong City Corporation",
    }
    await client.post(
        "/api/v1/employees/profile", json=profile_payload, headers=headers
    )

    # 3. Add monthly salary slips (e.g. 5 months)
    # Total monthly = 90,000 BDT. Over 5 months = 450,000 BDT gross.
    # Tax deducted at source monthly = 2,000 BDT (Total TDS = 10,000 BDT)
    # Provident fund = 5,000 BDT, Employer PF = 5,000 BDT (Total PF = 50,000 BDT)
    for m in range(7, 12):
        slip_payload = {
            "month": f"2024-{m:02d}",
            "basic_salary": "60000.00",
            "house_rent": "20000.00",
            "medical_allowance": "5000.00",
            "conveyance": "5000.00",
            "festival_bonus": "0.00",
            "provident_fund": "5000.00",
            "employer_provident_fund": "5000.00",
            "other_allowances": "10000.00",
            "tax_deducted": "2000.00",
        }
        res = await client.post(
            "/api/v1/salaries/slips", json=slip_payload, headers=headers
        )
        assert res.status_code == 201

    # 4. Add eligible investments
    # DPS of 120,000 BDT
    inv_payload = {
        "financial_year": "2024-2025",
        "category": "DPS",
        "amount": "120000.00",
        "description": "DPS log",
    }
    res_inv = await client.post(
        "/api/v1/investments/investments", json=inv_payload, headers=headers
    )
    assert res_inv.status_code == 201

    # 5. Add AIT paid logs
    # 15,000 BDT AIT
    ait_payload = {
        "financial_year": "2024-2025",
        "category": "Car Registration",
        "amount": "15000.00",
        "challan_number": "CH-12345",
        "description": "Car tax",
    }
    res_ait = await client.post(
        "/api/v1/investments/ait", json=ait_payload, headers=headers
    )
    assert res_ait.status_code == 201

    # 6. Run Dynamic Tax Calculation endpoint (without other income)
    # Total salary (5 months) = 525,000 BDT (including employer PF)
    # Exemption = 1/3 of 525,000 = 175,000 BDT.
    # Taxable salary = 350,000 BDT.
    # Since user is Female, her tax-free limit is 400,000 BDT under 2024-2025 rules.
    # Because 350,000 <= 400,000, gross tax should be 0.0 BDT!
    calc_payload = {"financial_year": "2024-2025", "other_income": "0.00"}
    res = await client.post(
        "/api/v1/taxes/calculate", json=calc_payload, headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert float(data["summary"]["total_salary"]) == 525000.0
    assert float(data["summary"]["exempted_salary"]) == 175000.0
    assert float(data["summary"]["taxable_salary"]) == 350000.0
    assert float(data["summary"]["gross_tax"]) == 0.0
    assert float(data["summary"]["net_tax"]) == 0.0

    # 7. Add other income of 250,000 BDT.
    # Total taxable income = 350,000 + 250,000 = 600,000 BDT.
    # Slabs for Female (threshold 400,000 BDT) under 2024-2025 rules:
    # - First 400,000 BDT: 0%
    # - Next 100,000 BDT: 5% (5,000 BDT tax)
    # - Next 100,000 BDT: 10% (10,000 BDT tax)
    # Gross tax should be 15,000 BDT!
    # Rebate:
    # PF = 50,000 BDT. Logged investments = 120,000 BDT. Total = 170,000 BDT.
    # Max eligible (20% of 600,000 BDT) = 120,000 BDT.
    # Investment rebate = min(15% of 120,000 = 18,000 BDT, 3% of 600,000 = 18,000 BDT, 10 Lakhs BDT) = 18,000 BDT.
    # Net tax (since gross tax after rebate is 0, local minimum tax of 5,000 BDT applies) = 5,000 BDT.
    # Final payable = 5,000 - 15,000 (AIT) - 10,000 (TDS) = -20,000 BDT (Refundable).
    calc_payload_other = {"financial_year": "2024-2025", "other_income": "250000.00"}
    res = await client.post(
        "/api/v1/taxes/calculate", json=calc_payload_other, headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert float(data["summary"]["total_taxable_income"]) == 600000.0
    assert float(data["summary"]["gross_tax"]) == 15000.0
    assert float(data["summary"]["eligible_investment"]) == 120000.0
    assert float(data["summary"]["investment_rebate"]) == 18000.0
    assert float(data["summary"]["minimum_tax"]) == 5000.0
    assert float(data["summary"]["net_tax"]) == 5000.0
    assert float(data["summary"]["ait_paid"]) == 15000.0
    assert float(data["summary"]["tds_salary"]) == 10000.0
    assert float(data["summary"]["final_payable"]) == -20000.0

    # 8. Calculate and Save calculation
    res = await client.post(
        "/api/v1/taxes/calculate-save", json=calc_payload_other, headers=headers
    )
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
    res = await client.get(
        f"/api/v1/taxes/history/{calc_id}/return/html", headers=headers
    )
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


@pytest.mark.asyncio
async def test_tax_engine_workflow_2025_2026(client: AsyncClient):
    # Tests the updated rules for 2025-2026 (10% rebate, 4.0L/4.25L slabs, flat 5000 min tax)
    register_payload = {
        "email": "unique_tax_engine_user_2526@example.com",
        "phone": "+8801799999998",
        "first_name": "Tax",
        "last_name": "Tester2",
        "password": "strongpassword",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "unique_tax_engine_user_2526@example.com",
            "password": "strongpassword",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Setup employee profile (Female)
    profile_payload = {
        "designation": "Staff Developer",
        "department": "Engineering",
        "nid": "112233445567",
        "gender": "Female",
        "location": "Dhaka/Chittagong City Corporation",
    }
    await client.post(
        "/api/v1/employees/profile", json=profile_payload, headers=headers
    )

    # Add monthly salary slips (5 months)
    for m in range(7, 12):
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
            "tax_deducted": "2000.00",
        }
        await client.post("/api/v1/salaries/slips", json=slip_payload, headers=headers)

    # Add eligible investments
    inv_payload = {
        "financial_year": "2025-2026",
        "category": "DPS",
        "amount": "120000.00",
        "description": "DPS log",
    }
    await client.post(
        "/api/v1/investments/investments", json=inv_payload, headers=headers
    )

    # Add AIT paid logs (15,000 BDT)
    ait_payload = {
        "financial_year": "2025-2026",
        "category": "Car Registration",
        "amount": "15000.00",
        "challan_number": "CH-12345",
        "description": "Car tax",
    }
    await client.post("/api/v1/investments/ait", json=ait_payload, headers=headers)

    # Run dynamic tax calculation (with other income of 250,000 BDT)
    # Total taxable income = 350,000 (taxable salary) + 250,000 = 600,000 BDT.
    # Slabs for Female (threshold 425,000 BDT) under 2025-2026 rules:
    # - First 425,000 BDT: 0%
    # - Next 175,000 BDT: 10% (17,500 BDT gross tax)
    # Total gross tax = 17,500 BDT.
    # Rebate:
    # Eligible investment = 1,20,000 BDT.
    # Investment rebate = min(10% of 120k = 12,000 BDT, 3% of 600k = 18,000 BDT, 7,50,000 BDT) = 12,000 BDT.
    # Tax after rebate = 17,500 - 12,000 = 5,500 BDT.
    # Net tax = 5,500 BDT (since 5,500 >= flat 5,000 minimum tax limit).
    # Final payable = 5,500 - 15,000 (AIT) - 10,000 (TDS) = -19,500 BDT (Refundable).
    calc_payload_other = {"financial_year": "2025-2026", "other_income": "250000.00"}
    res = await client.post(
        "/api/v1/taxes/calculate", json=calc_payload_other, headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert float(data["summary"]["total_taxable_income"]) == 600000.0
    assert float(data["summary"]["gross_tax"]) == 17500.0
    assert float(data["summary"]["eligible_investment"]) == 120000.0
    assert float(data["summary"]["investment_rebate"]) == 12000.0
    assert float(data["summary"]["minimum_tax"]) == 5000.0
    assert float(data["summary"]["net_tax"]) == 5500.0
    assert float(data["summary"]["ait_paid"]) == 15000.0
    assert float(data["summary"]["tds_salary"]) == 10000.0
    assert float(data["summary"]["final_payable"]) == -19500.0
