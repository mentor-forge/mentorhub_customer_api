"""
E2E tests for Journey endpoints (by-id only).

These tests verify that Journey endpoints work correctly by making
actual HTTP requests to a running server.

To run these tests:
1. Start the server: pipenv run dev (or pipenv run api for containerized)
2. Run E2E tests: pipenv run e2e

API runs on port 8387 (same for dev and api).
"""

import pytest
import requests

from .e2e_auth import get_auth_token

BASE_URL = "http://localhost:8387"


def _err(response, expected):
    """Format assertion error with response body for debugging."""
    body = response.text[:300] if response.text else "(empty)"
    return f"Expected {expected}, got {response.status_code}. Response: {body}"


@pytest.mark.e2e
def test_get_journeys_list_returns_404():
    """Test GET /api/journey endpoint returns 404 (by-id only)."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/journey", headers=headers)
    assert response.status_code == 404, _err(response, 404)


@pytest.mark.e2e
def test_get_journey_not_found():
    """Test GET /api/journey/<id> with non-existent ID."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/journey/000000000000000000000000",
        headers=headers,
    )
    assert response.status_code == 404, _err(response, 404)


@pytest.mark.e2e
def test_journey_endpoints_require_auth():
    """Test that journey endpoints require authentication."""
    response = requests.get(f"{BASE_URL}/api/journey/507f1f77bcf86cd799439011")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
