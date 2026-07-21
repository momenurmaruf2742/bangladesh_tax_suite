import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration endpoint."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "phone": "+8801712345678",
            "first_name": "Momenur",
            "last_name": "Islam",
            "tin": "123456789012",
            "password": "securepassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["first_name"] == "Momenur"
    assert "id" in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test user registration prevents duplicate emails."""
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "phone": "+8801700000001",
            "first_name": "First",
            "last_name": "User",
            "password": "password123"
        }
    )
    
    # Second registration with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "phone": "+8801700000002",
            "first_name": "Second",
            "last_name": "User",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test login functionality with correct and incorrect credentials."""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "phone": "+8801711111111",
            "first_name": "Login",
            "last_name": "User",
            "password": "loginpassword"
        }
    )
    
    # Login with email
    response_email = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser@example.com",
            "password": "loginpassword"
        }
    )
    assert response_email.status_code == 200
    data_email = response_email.json()
    assert "access_token" in data_email
    assert "refresh_token" in data_email
    
    # Login with phone
    response_phone = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "+8801711111111",
            "password": "loginpassword"
        }
    )
    assert response_phone.status_code == 200
    
    # Login with wrong password
    response_wrong = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser@example.com",
            "password": "wrongpassword"
        }
    )
    assert response_wrong.status_code == 401


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient):
    """Test getting profile using access token."""
    # Register and Login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "profileuser@example.com",
            "phone": "+8801722222222",
            "first_name": "Profile",
            "last_name": "User",
            "password": "profilepassword"
        }
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "profileuser@example.com",
            "password": "profilepassword"
        }
    )
    token = login_resp.json()["access_token"]
    
    # Request profile
    response = await client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "profileuser@example.com"
