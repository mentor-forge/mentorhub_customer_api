"""
E2E tests for Subscription endpoints.

These tests verify that Subscription endpoints work correctly by making
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
def test_create_subscription_endpoint():
    """Test POST /api/subscription endpoint and verify record persists in database."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "e2e-test-subscription",
        "description": "E2E test subscription document",
    }

    response = requests.post(f"{BASE_URL}/api/subscription", headers=headers, json=data)
    assert response.status_code == 201, _err(response, 201)

    response_data = response.json()
    assert "_id" in response_data, "Response missing '_id' key"
    assert response_data["name"] == "e2e-test-subscription"
    assert "created" in response_data
    assert "saved" in response_data


@pytest.mark.e2e
def test_get_subscriptions_endpoint():
    """Test GET /api/subscription endpoint."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/subscription", headers=headers)
    assert response.status_code == 200, _err(response, 200)

    response_data = response.json()
    assert isinstance(response_data, dict), "Response should be a dict (infinite scroll format)"
    assert "items" in response_data, "Response should have 'items' key"
    assert "limit" in response_data, "Response should have 'limit' key"
    assert "has_more" in response_data, "Response should have 'has_more' key"
    assert "next_cursor" in response_data, "Response should have 'next_cursor' key"
    assert isinstance(response_data["items"], list), "Items should be a list"


@pytest.mark.e2e
def test_get_subscriptions_with_name_filter():
    """Test GET /api/subscription with name query parameter."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/subscription?name=e2e", headers=headers)
    assert response.status_code == 200, _err(response, 200)

    response_data = response.json()
    assert isinstance(response_data, dict), "Response should be a dict (infinite scroll format)"
    assert "items" in response_data, "Response should have 'items' key"
    assert isinstance(response_data["items"], list), "Items should be a list"


@pytest.mark.e2e
def test_subscription_endpoints_require_auth():
    """Test that subscription endpoints require authentication."""
    response = requests.get(f"{BASE_URL}/api/subscription")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
