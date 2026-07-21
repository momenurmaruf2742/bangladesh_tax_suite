import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_employer_and_employee_flow(client: AsyncClient):
    # 1. Register and login Admin
    admin_register_payload = {
        "email": "admin@example.com",
        "phone": "+8801700000001",
        "first_name": "System",
        "last_name": "Admin",
        "password": "adminpassword"
    }
    res = await client.post("/api/v1/auth/register", json=admin_register_payload)
    assert res.status_code == 201
    
    # Manually promote registered user to Admin for tests
    # (Since there's no UI for it yet, and role defaults to Employee, we register another standard user to compare role access)
    
    # 2. Register and login standard Employee
    employee_register_payload = {
        "email": "employee@example.com",
        "phone": "+8801700000002",
        "first_name": "Momenur",
        "last_name": "Islam",
        "password": "employeepassword",
        "tin": "123456789012"
    }
    res = await client.post("/api/v1/auth/register", json=employee_register_payload)
    assert res.status_code == 201
    
    # Login Employee
    res = await client.post("/api/v1/auth/login", json={
        "username": "employee@example.com",
        "password": "employeepassword"
    })
    assert res.status_code == 200
    emp_token = res.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # Login Admin (We'll use another user and test with Admin role)
    # First, let's login admin (currently has Employee role in db, but we can verify standard user restrictions)
    res = await client.post("/api/v1/auth/login", json={
        "username": "admin@example.com",
        "password": "adminpassword"
    })
    assert res.status_code == 200
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Standard Employee tries to create an Employer -> Should fail with 403 (since default role is Employee)
    employer_payload = {
        "name": "Bangladesh Technology Ltd",
        "address": "Gulshan, Dhaka",
        "bin": "123456789",
        "contact_email": "info@bdtech.com",
        "contact_phone": "+8801711111111"
    }
    res = await client.post("/api/v1/employers/", json=employer_payload, headers=emp_headers)
    assert res.status_code == 403  # Forbidden

    # For testing CA/Admin routes, let's register a user and update their role in database,
    # or we can test that standard employees can view, but cannot modify.
    # Let's check listing employers (should be empty but return 200)
    res = await client.get("/api/v1/employers/", headers=emp_headers)
    assert res.status_code == 200
    assert len(res.json()) == 0


@pytest.mark.asyncio
async def test_employee_profile_operations(client: AsyncClient):
    # Register and login user
    register_payload = {
        "email": "momenur.tax@example.com",
        "phone": "+8801700000003",
        "first_name": "Momenur",
        "last_name": "Islam",
        "password": "secretpassword"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_res = await client.post("/api/v1/auth/login", json={
        "username": "momenur.tax@example.com",
        "password": "secretpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to fetch profile before setting it up -> Should return 404
    res = await client.get("/api/v1/employees/profile", headers=headers)
    assert res.status_code == 404

    # Setup employee profile
    profile_payload = {
        "designation": "Lead Software Engineer",
        "department": "IT Division",
        "date_of_joining": "2024-01-15",
        "nid": "1234567890",
        "tax_zone": "Zone 12, Dhaka",
        "tax_circle": "Circle 240"
    }
    res = await client.post("/api/v1/employees/profile", json=profile_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["designation"] == "Lead Software Engineer"
    assert data["nid"] == "1234567890"
    assert data["user"]["email"] == "momenur.tax@example.com"
    assert data["employer"] is None

    # Fetch profile again -> Should now return 200 OK
    res = await client.get("/api/v1/employees/profile", headers=headers)
    assert res.status_code == 200
    assert res.json()["designation"] == "Lead Software Engineer"

    # List employees as standard employee -> Should return 403 Forbidden
    res = await client.get("/api/v1/employees/", headers=headers)
    assert res.status_code == 403
