"""Tests for user profile retrieval, update, and protected endpoint access."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_current_user_profile_success(client: AsyncClient) -> None:
    """Verify /users/me returns authenticated user's profile."""
    # Register & Login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "profile@example.com", "password": "Password123!", "full_name": "Profile User"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "profile@example.com", "password": "Password123!"},
    )
    access_token = login_res.json()["access_token"]

    # Fetch profile
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["full_name"] == "Profile User"
    assert data["base_currency"] == "INR"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized_without_token(client: AsyncClient) -> None:
    """Verify /users/me returns 401 when no token is provided."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "NOT_AUTHENTICATED"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient) -> None:
    """Verify /users/me returns 401 when an invalid/garbage token is provided."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_update_user_profile_success(client: AsyncClient) -> None:
    """Verify /users/me PATCH updates user profile fields."""
    # Register & Login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "updater@example.com", "password": "Password123!", "full_name": "Old Name", "base_currency": "INR"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "updater@example.com", "password": "Password123!"},
    )
    access_token = login_res.json()["access_token"]

    # Update profile
    patch_res = await client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"full_name": "New Name", "base_currency": "USD"},
    )
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["full_name"] == "New Name"
    assert updated_data["base_currency"] == "USD"

    # Verify subsequent GET returns the updated profile
    get_res = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_res.json()["full_name"] == "New Name"
    assert get_res.json()["base_currency"] == "USD"


@pytest.mark.asyncio
async def test_user_cannot_access_or_update_other_users_data(client: AsyncClient) -> None:
    """Verify endpoint isolation: User A's token can only access and modify User A's data."""
    # User A
    await client.post(
        "/api/v1/auth/register",
        json={"email": "usera@example.com", "password": "Password123!", "full_name": "User A"},
    )
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": "usera@example.com", "password": "Password123!"},
    )
    token_a = login_a.json()["access_token"]

    # User B
    await client.post(
        "/api/v1/auth/register",
        json={"email": "userb@example.com", "password": "Password123!", "full_name": "User B"},
    )
    login_b = await client.post(
        "/api/v1/auth/login",
        json={"email": "userb@example.com", "password": "Password123!"},
    )
    token_b = login_b.json()["access_token"]

    # Requesting /me with token A returns User A
    res_a = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.json()["email"] == "usera@example.com"

    # Requesting /me with token B returns User B
    res_b = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.json()["email"] == "userb@example.com"

    # User A updates their profile
    await client.patch("/api/v1/users/me", headers={"Authorization": f"Bearer {token_a}"}, json={"full_name": "Updated User A"})

    # User B's profile remains untouched
    res_b_after = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b_after.json()["full_name"] == "User B"
