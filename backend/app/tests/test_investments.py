import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_investments_and_ait_workflow(client: AsyncClient):
    # 1. Register and login user
    register_payload = {
        "email": "invest.user@example.com",
        "phone": "+8801744444444",
        "first_name": "Invest",
        "last_name": "Tester",
        "password": "strongpassword"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_res = await client.post("/api/v1/auth/login", json={
        "username": "invest.user@example.com",
        "password": "strongpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup employee profile
    profile_payload = {
        "designation": "Manager",
        "nid": "5566778899"
    }
    await client.post("/api/v1/employees/profile", json=profile_payload, headers=headers)

    # 3. Create investments
    inv_dps = {
        "financial_year": "2025-2026",
        "category": "DPS",
        "amount": "100000.00",
        "description": "Monthly DPS contribution"
    }
    res = await client.post("/api/v1/investments/investments", json=inv_dps, headers=headers)
    assert res.status_code == 201
    assert res.json()["category"] == "DPS"
    assert float(res.json()["amount"]) == 100000.0

    inv_life = {
        "financial_year": "2025-2026",
        "category": "Life Insurance",
        "amount": "50000.00",
        "description": "MetLife Premium"
    }
    await client.post("/api/v1/investments/investments", json=inv_life, headers=headers)

    # 4. List investments -> verify length 2
    res = await client.get("/api/v1/investments/investments", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2

    # 5. Create AIT records
    ait_car = {
        "financial_year": "2025-2026",
        "category": "Car Registration",
        "amount": "15000.00",
        "challan_number": "CH-123456",
        "challan_date": "2025-10-15",
        "description": "BRTA advance tax"
    }
    res = await client.post("/api/v1/investments/ait", json=ait_car, headers=headers)
    assert res.status_code == 201
    assert res.json()["challan_number"] == "CH-123456"
    assert float(res.json()["amount"]) == 15000.0

    ait_bank = {
        "financial_year": "2025-2026",
        "category": "Bank Interest TDS",
        "amount": "5000.00",
        "description": "MTB source tax deduction"
    }
    await client.post("/api/v1/investments/ait", json=ait_bank, headers=headers)

    # 6. List AIT records -> verify length 2
    res = await client.get("/api/v1/investments/ait", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2

    # 7. Get rebate summary -> verify totals
    res = await client.get("/api/v1/investments/summary?financial_year=2025-2026", headers=headers)
    assert res.status_code == 200
    summary = res.json()
    assert float(summary["total_invested"]) == 150000.0
    assert float(summary["total_ait"]) == 20000.0
    assert float(summary["dps_total"]) == 100000.0
    assert float(summary["life_insurance_total"]) == 50000.0

    # 8. Update investment record
    invest_id = res.json() # wait, get id from list
    res_list = await client.get("/api/v1/investments/investments", headers=headers)
    first_id = res_list.json()[0]["id"]
    
    update_payload = {"amount": "120000.00"}
    res = await client.put(f"/api/v1/investments/investments/{first_id}", json=update_payload, headers=headers)
    assert res.status_code == 200
    assert float(res.json()["amount"]) == 120000.0

    # 9. Delete investment record
    res = await client.delete(f"/api/v1/investments/investments/{first_id}", headers=headers)
    assert res.status_code == 204
