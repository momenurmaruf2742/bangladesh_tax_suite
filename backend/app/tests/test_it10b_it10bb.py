from decimal import Decimal
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_it10bb_lifestyle_expenses_workflow(client: AsyncClient):
    # 1. Register and login
    register_payload = {
        "email": "it10bb_user@example.com",
        "phone": "+8801811111111",
        "first_name": "Rahim",
        "last_name": "Uddin",
        "password": "strongpassword",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "it10bb_user@example.com",
            "password": "strongpassword",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup employee profile
    profile_payload = {
        "designation": "Software Engineer",
        "department": "Engineering",
        "nid": "9876543210123",
        "gender": "Male",
        "location": "Dhaka/Chittagong City Corporation",
    }
    await client.post(
        "/api/v1/employees/profile", json=profile_payload, headers=headers
    )

    # 3. Add salary slips with TDS to test automatic ledger synchronization
    # Add a salary slip with 9,542 BDT TDS
    slip_payload = {
        "month": "2025-07",
        "basic_salary": "50000.00",
        "house_rent": "25000.00",
        "medical_allowance": "5000.00",
        "conveyance": "5000.00",
        "festival_bonus": "0.00",
        "provident_fund": "5000.00",
        "employer_provident_fund": "5000.00",
        "other_allowances": "0.00",
        "tax_deducted": "9542.00",
    }
    res_slip = await client.post("/api/v1/salaries/slips", json=slip_payload, headers=headers)
    assert res_slip.status_code == 201

    # 4. Save IT-10BB Lifestyle Expenses matching Return-531631892211.pdf audit values:
    # Essentials: 1,50,000; House Rent: 70,000; Transport: 50,000; Utility: 49,000; Festival: 50,000
    # Auto-synced Line 8 TDS: 9,542
    # Expected Total: 1,50,000 + 70,000 + 50,000 + 49,000 + 50,000 + 9,542 = 3,78,542
    expense_payload = {
        "financial_year": "2025-2026",
        "fooding_clothing_essentials": "150000.00",
        "housing_expense": "70000.00",
        "transport_expense": "50000.00",
        "utility_expense": "49000.00",
        "education_expenses": "0.00",
        "travel_vacation_expenses": "0.00",
        "festival_special_expenses": "50000.00",
        "interest_paid_borrowing": "0.00",
        "other_expenses": "0.00",
        "auto_synced_tds": True,
    }
    res_save = await client.post("/api/v1/taxes/it10bb", json=expense_payload, headers=headers)
    assert res_save.status_code == 200
    saved = res_save.json()
    assert Decimal(str(saved["fooding_clothing_essentials"])) == Decimal("150000.00")
    assert Decimal(str(saved["tax_deducted_source_advance"])) == Decimal("9542.00")
    assert Decimal(str(saved["total_lifestyle_expense"])) == Decimal("378542.00")
    assert saved["assessment_year"] == "2026-2027"

    # 5. Fetch IT-10BB via GET
    res_get = await client.get("/api/v1/taxes/it10bb?financial_year=2025-2026", headers=headers)
    assert res_get.status_code == 200
    fetched = res_get.json()
    assert Decimal(str(fetched["total_lifestyle_expense"])) == Decimal("378542.00")


@pytest.mark.asyncio
async def test_it10b_wealth_reconciliation_exact_audit_parity(client: AsyncClient):
    # Tests mathematical parity with Return-531631892211.pdf:
    # Taxable income: 6,71,533
    # Tax-exempted income: 3,35,767
    # Total source of fund: 10,07,300
    # Net wealth (previous year): 1,27,758
    # Lifestyle expenses: 3,78,542
    # Closing net wealth: 7,56,516
    # Change in net wealth: 7,56,516 - 1,27,758 = 6,28,758
    # Total outflow: 6,28,758 + 3,78,542 = 10,07,300
    # Difference: 10,07,300 - 10,07,300 = 0.00 (Balanced!)

    register_payload = {
        "email": "it10b_audit_user@example.com",
        "phone": "+8801822222222",
        "first_name": "Audit",
        "last_name": "Verified",
        "password": "strongpassword",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "it10b_audit_user@example.com",
            "password": "strongpassword",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Preview reconciliation via /reconcile endpoint
    preview_payload = {
        "financial_year": "2025-2026",
        "taxable_income": "671533.00",
        "tax_exempted_income": "335767.00",
        "gifts_and_other_receipts": "0.00",
        "net_wealth_previous_year": "127758.00",
        "lifestyle_expenses": "378542.00",
        "other_outflow_losses": "0.00",
        # Assets totaling 7,56,516 closing wealth:
        "financial_assets_dps": "80000.00",
        "furniture_electronics_value": "100000.00",
        "cash_in_hand": "276516.00",
        "bank_balances": "300000.00",
        "institutional_liabilities": "0.00",
        "non_institutional_liabilities": "0.00",
    }
    res_preview = await client.post("/api/v1/taxes/it10b/reconcile", json=preview_payload, headers=headers)
    assert res_preview.status_code == 200
    preview = res_preview.json()
    assert Decimal(str(preview["total_fund_inflow"])) == Decimal("1007300.00")
    assert Decimal(str(preview["gross_wealth"])) == Decimal("756516.00")
    assert Decimal(str(preview["net_wealth_closing"])) == Decimal("756516.00")
    assert Decimal(str(preview["change_in_net_wealth"])) == Decimal("628758.00")
    assert Decimal(str(preview["total_fund_outflow"])) == Decimal("1007300.00")
    assert Decimal(str(preview["difference"])) == Decimal("0.00")
    assert preview["is_balanced"] is True

    # 2. Save IT-10B Statement to database
    res_save = await client.post("/api/v1/taxes/it10b", json=preview_payload, headers=headers)
    assert res_save.status_code == 200
    saved = res_save.json()
    stmt_id = saved["id"]
    assert saved["is_balanced"] is True
    assert Decimal(str(saved["difference"])) == Decimal("0.00")
    assert saved["assessment_year"] == "2026-2027"

    # 3. Add Motor Vehicle acquired as Gift (Cost = 0.00, Section 3.4 of audit)
    gift_bike_payload = {
        "asset_category": "motor_vehicles",
        "description": "Dhaka Metro LA 67-6774 Motorcycle 155 CC",
        "acquisition_type": "Gift",
        "cost_value": "0.00",
        "particulars": {
            "vehicle_type": "Motorcycle",
            "registration_no": "Dhaka Metro LA 67-6774",
            "engine_capacity": "155 CC",
        },
    }
    res_bike = await client.post(f"/api/v1/taxes/it10b/{stmt_id}/assets", json=gift_bike_payload, headers=headers)
    assert res_bike.status_code == 200
    bike = res_bike.json()
    assert bike["acquisition_type"] == "Gift"
    assert Decimal(str(bike["cost_value"])) == Decimal("0.00")
    assert bike["particulars"]["engine_capacity"] == "155 CC"

    # 4. Add Gold and Silver acquired as Gift (Cost = 0.00)
    gift_gold_payload = {
        "asset_category": "ornaments_gold",
        "description": "Gold 4.75 Gram & Silver 2.2 Bhori",
        "acquisition_type": "Gift",
        "cost_value": "0.00",
        "particulars": {
            "gold_gram": 4.75,
            "silver_bhori": 2.2,
        },
    }
    res_gold = await client.post(f"/api/v1/taxes/it10b/{stmt_id}/assets", json=gift_gold_payload, headers=headers)
    assert res_gold.status_code == 200
    gold_item_id = res_gold.json()["id"]

    # 5. Fetch IT-10B Statement including detailed asset items
    res_get = await client.get("/api/v1/taxes/it10b?financial_year=2025-2026", headers=headers)
    assert res_get.status_code == 200
    full_stmt = res_get.json()
    assert len(full_stmt["asset_items"]) == 2
    assert full_stmt["is_balanced"] is True

    # 6. Delete an asset item
    res_del = await client.delete(f"/api/v1/taxes/it10b/assets/{gold_item_id}", headers=headers)
    assert res_del.status_code == 204

    # Verify only 1 asset remains
    res_items = await client.get(f"/api/v1/taxes/it10b/{stmt_id}/assets", headers=headers)
    assert res_items.status_code == 200
    assert len(res_items.json()) == 1


@pytest.mark.asyncio
async def test_it10b_auto_balance_cash_in_hand(client: AsyncClient):
    # Test that auto_balance_cash_in_hand closes residual gaps
    register_payload = {
        "email": "it10b_autobalance@example.com",
        "phone": "+8801833333333",
        "first_name": "Cash",
        "last_name": "Balancer",
        "password": "strongpassword",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "it10b_autobalance@example.com",
            "password": "strongpassword",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Save statement with an unbalanced gap (e.g. Inflow = 500,000, Assets + Outflow = 400,000 -> Diff = 100,000)
    unbalanced_payload = {
        "financial_year": "2025-2026",
        "taxable_income": "500000.00",
        "tax_exempted_income": "0.00",
        "net_wealth_previous_year": "0.00",
        "lifestyle_expenses": "200000.00",
        "bank_balances": "200000.00",
        "cash_in_hand": "0.00",
    }
    res_save = await client.post("/api/v1/taxes/it10b", json=unbalanced_payload, headers=headers)
    assert res_save.status_code == 200
    saved = res_save.json()
    assert saved["is_balanced"] is False
    assert Decimal(str(saved["difference"])) == Decimal("100000.00")

    # Call auto-balance endpoint
    res_auto = await client.post("/api/v1/taxes/it10b/auto-balance-cash?financial_year=2025-2026", headers=headers)
    assert res_auto.status_code == 200
    auto_data = res_auto.json()
    assert auto_data["is_balanced"] is True
    assert Decimal(str(auto_data["adjusted_cash_in_hand"])) == Decimal("100000.00")

    # Verify statement in DB is now balanced
    res_get = await client.get("/api/v1/taxes/it10b?financial_year=2025-2026", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["is_balanced"] is True
    assert Decimal(str(res_get.json()["difference"])) == Decimal("0.00")
