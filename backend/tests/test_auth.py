"""Comprehensive tests for authentication: registration, login, token refresh, and logout."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient) -> None:
    """Verify new user registration succeeds with valid data."""
    payload = {
        "email": "alice@example.com",
        "password": "StrongPassword123!",
        "full_name": "Alice Sharma",
        "base_currency": "INR",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Sharma"
    assert data["base_currency"] == "INR"
    assert data["is_active"] is True
    # Ensure password hash is NEVER leaked in response
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_user_registration_duplicate_email_fails(client: AsyncClient) -> None:
    """Verify registration fails with 409 Conflict when email is already registered."""
    payload = {
        "email": "duplicate@example.com",
        "password": "Password1234!",
        "full_name": "First User",
        "base_currency": "INR",
    }
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt to register again with same email (different case)
    payload["email"] = "DUPLICATE@example.com"
    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    err = res2.json()
    assert err["code"] == "EMAIL_ALREADY_EXISTS"
    assert "already registered" in err["detail"].lower()


@pytest.mark.asyncio
async def test_user_registration_validation_errors(client: AsyncClient) -> None:
    """Verify input validation constraints on registration."""
    # 1. Short password (< 8 chars)
    res = await client.post(
        "/api/v1/auth/register",
        json={"email": "val1@example.com", "password": "short", "full_name": "Val User"},
    )
    assert res.status_code == 422
    assert res.json()["code"] == "VALIDATION_ERROR"

    # 2. Blank full_name
    res = await client.post(
        "/api/v1/auth/register",
        json={"email": "val2@example.com", "password": "Password123!", "full_name": "   "},
    )
    assert res.status_code == 422

    # 3. Invalid currency format
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "val3@example.com",
            "password": "Password123!",
            "full_name": "Val User",
            "base_currency": "INVALID",
        },
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient) -> None:
    """Verify valid credentials return access and refresh tokens."""
    # Register user first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "loginuser@example.com", "password": "Password123!", "full_name": "Login User"},
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "LOGINUSER@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 900


@pytest.mark.asyncio
async def test_user_login_invalid_credentials(client: AsyncClient) -> None:
    """Verify 401 Unauthorized for wrong password or non-existent user."""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "bob@example.com", "password": "CorrectPassword123!", "full_name": "Bob"},
    )

    # Wrong password
    res1 = await client.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "WrongPassword!"},
    )
    assert res1.status_code == 401
    assert res1.json()["code"] == "INVALID_CREDENTIALS"

    # Non-existent email
    res2 = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123!"},
    )
    assert res2.status_code == 401
    assert res2.json()["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_refresh_token_rotation_success(client: AsyncClient) -> None:
    """Verify token refresh issues a new access token and a rotated refresh token."""
    # Register & login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "rotator@example.com", "password": "Password123!", "full_name": "Rotator"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "rotator@example.com", "password": "Password123!"},
    )
    first_refresh_token = login_res.json()["refresh_token"]

    # Perform refresh
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    # Crucial: the refresh token MUST have rotated
    assert new_data["refresh_token"] != first_refresh_token


@pytest.mark.asyncio
async def test_token_reuse_detection_triggers_family_revocation(client: AsyncClient) -> None:
    """Verify that reusing a consumed refresh token invalidates the entire token family."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "reuser@example.com", "password": "Password123!", "full_name": "Reuser"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "reuser@example.com", "password": "Password123!"},
    )
    first_token = login_res.json()["refresh_token"]

    # Legitimate first rotation
    rot_res1 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_token},
    )
    assert rot_res1.status_code == 200
    second_token = rot_res1.json()["refresh_token"]

    # Attacker or replay attempts to use the FIRST token again!
    reuse_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_token},
    )
    assert reuse_res.status_code == 401
    assert reuse_res.json()["code"] == "TOKEN_REUSE_DETECTED"

    # Now, even the valid second token must be invalidated because the family is compromised!
    second_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": second_token},
    )
    assert second_res.status_code == 401
    assert second_res.json()["code"] == "TOKEN_REUSE_DETECTED"


@pytest.mark.asyncio
async def test_logout_revokes_session(client: AsyncClient) -> None:
    """Verify logging out revokes the refresh token."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "logoutuser@example.com", "password": "Password123!", "full_name": "Logout User"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "logoutuser@example.com", "password": "Password123!"},
    )
    tokens = login_res.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Logout
    logout_res = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == 204

    # Subsequent refresh attempt with revoked token must fail
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 401
