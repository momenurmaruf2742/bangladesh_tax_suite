import pytest
from app.modules.taxes.model import TaxRule
from app.modules.users.model import User
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.asyncio
async def test_dynamic_rules_workflow(client: AsyncClient, db_session: AsyncSession):
    # 1. Register and login a standard user
    register_payload = {
        "email": "rules_admin@example.com",
        "phone": "+8801700100001",
        "first_name": "Rules",
        "last_name": "Admin",
        "password": "rulespassword",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    # 2. Promote the user to Admin in database
    statement = select(User).where(User.email == "rules_admin@example.com")
    result = await db_session.exec(statement)
    user = result.first()
    assert user is not None
    user.role = "Admin"
    db_session.add(user)
    await db_session.commit()

    # 3. Login the Admin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "rules_admin@example.com",
            "password": "rulespassword",
        },
    )
    token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {token}"}

    # 4. Expose standard user register for comparison
    employee_payload = {
        "email": "standard_rules_user@example.com",
        "phone": "+8801700100002",
        "first_name": "Standard",
        "last_name": "User",
        "password": "rulespassword",
    }
    await client.post("/api/v1/auth/register", json=employee_payload)
    login_res_emp = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "standard_rules_user@example.com",
            "password": "rulespassword",
        },
    )
    emp_token = login_res_emp.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # 5. List rules (should default auto-seed the 3 standard years)
    res = await client.get("/api/v1/taxes/rules", headers=emp_headers)
    assert res.status_code == 200
    assert len(res.json()) == 3

    # 6. Create custom rule (Standard employee should be blocked with 403)
    rule_create_payload = {
        "financial_year": "2027-2028",
        "exemption_rate": "3.0",
        "exemption_max": "450000.00",
        "dps_max": "150000.00",
        "rebate_rate": "0.10",
        "income_rebate_limit_rate": "0.03",
        "max_rebate_cap": "750000.00",
        "max_eligible_invest_rate": "0.20",
        "max_eligible_invest_cap": "7500000.00",
        "thresholds": {
            "default": "400000.00",
            "Female": "425000.00",
            "Third Gender": "425000.00",
            "is_disabled": "475000.00",
            "is_freedom_fighter": "525000.00",
        },
        "slabs": [
            ["Tax-free limit", 0, 0],
            ["Next 3,00,000 BDT", 300000, 0.10],
            ["Remaining taxable balance", None, 0.30],
        ],
        "minimum_tax_location_based": False,
        "minimum_tax": {"default": "5000.00"},
    }

    res_post_block = await client.post(
        "/api/v1/taxes/rules", json=rule_create_payload, headers=emp_headers
    )
    assert res_post_block.status_code == 403

    # 7. Create custom rule (Admin should succeed)
    res_post = await client.post(
        "/api/v1/taxes/rules", json=rule_create_payload, headers=admin_headers
    )
    assert res_post.status_code == 201
    assert res_post.json()["financial_year"] == "2027-2028"

    # 8. List rules again (should contain 4 rules now)
    res_list = await client.get("/api/v1/taxes/rules", headers=emp_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 4
    custom_rule = next(r for r in res_list.json() if r["financial_year"] == "2027-2028")
    assert float(custom_rule["dps_max"]) == 150000.0

    # 9. Get specific rule by year
    res_get = await client.get("/api/v1/taxes/rules/2027-2028", headers=emp_headers)
    assert res_get.status_code == 200
    assert res_get.json()["financial_year"] == "2027-2028"

    # 10. Update rule (Admin change dps_max to 2,00,000)
    rule_update_payload = {"dps_max": "200000.00"}
    res_put = await client.put(
        "/api/v1/taxes/rules/2027-2028", json=rule_update_payload, headers=admin_headers
    )
    assert res_put.status_code == 200
    assert float(res_put.json()["dps_max"]) == 200000.0

    # 11. Delete rule (Standard employee should be blocked, Admin should succeed)
    res_del_block = await client.delete(
        "/api/v1/taxes/rules/2027-2028", headers=emp_headers
    )
    assert res_del_block.status_code == 403

    res_del = await client.delete(
        "/api/v1/taxes/rules/2027-2028", headers=admin_headers
    )
    assert res_del.status_code == 204
