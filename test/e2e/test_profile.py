"""
E2E tests for Profile endpoints (Customer control).

These tests verify that Profile endpoints work correctly by making
actual HTTP requests to a running server.

To run these tests:
1. Start the server: pipenv run dev (or pipenv run api for containerized)
2. Run E2E tests: pipenv run e2e

API runs on port 8387 (same for dev and api).
"""

import time
import pytest
import requests

from .e2e_auth import get_auth_token

BASE_URL = "http://localhost:8387"


def _err(response, expected):
    """Format assertion error with response body for debugging."""
    body = response.text[:300] if response.text else "(empty)"
    return f"Expected {expected}, got {response.status_code}. Response: {body}"


@pytest.mark.e2e
def test_get_profiles_endpoint():
    """Test GET /api/profile endpoint."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/profile", headers=headers)
    assert response.status_code == 200, _err(response, 200)

    response_data = response.json()
    assert isinstance(response_data, list), "Response should be a list"


@pytest.mark.e2e
def test_get_profiles_with_display_name_filter():
    """Test GET /api/profile with display_name query parameter."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/profile?display_name=Test", headers=headers
    )
    assert response.status_code == 200, _err(response, 200)

    response_data = response.json()
    assert isinstance(response_data, list), "Response should be a list"


@pytest.mark.e2e
def test_create_and_patch_profile_endpoint():
    """Test POST /api/profile and PATCH /api/profile/<id>."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    create_data = {
        "display_name": f"E2E User {int(time.time())}",
        "email": "e2e@example.com",
        "description": "Initial description",
    }
    create_res = requests.post(
        f"{BASE_URL}/api/profile", headers=headers, json=create_data
    )
    assert create_res.status_code == 201, _err(create_res, 201)
    profile = create_res.json()
    profile_id = profile["_id"]
    assert profile["description"] == "Initial description"

    patch_data = {"description": "Updated description"}
    patch_res = requests.patch(
        f"{BASE_URL}/api/profile/{profile_id}", headers=headers, json=patch_data
    )
    assert patch_res.status_code == 200, _err(patch_res, 200)
    updated = patch_res.json()
    assert updated["description"] == "Updated description"


@pytest.mark.e2e
def test_get_profile_not_found():
    """Test GET /api/profile/<id> with non-existent ID."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/profile/000000000000000000000000",
        headers=headers,
    )
    assert response.status_code == 404, _err(response, 404)


@pytest.mark.e2e
def test_profile_endpoints_require_auth():
    """Test that profile endpoints require authentication."""
    response = requests.get(f"{BASE_URL}/api/profile")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
