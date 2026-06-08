"""
Unit tests for Subscription routes.

These tests validate the Flask route layer for the Subscription domain, using the
generated blueprint factory and mocking out the underlying service and
token/breadcrumb helpers from api_utils.
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.subscription_routes import create_subscription_routes


class TestSubscriptionRoutes(unittest.TestCase):
    """Test cases for Subscription routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_subscription_routes(),
            url_prefix="/api/subscription",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.subscription_routes.create_flask_token")
    @patch("src.routes.subscription_routes.create_flask_breadcrumb")
    @patch("src.routes.subscription_routes.SubscriptionService.create_subscription")
    @patch("src.routes.subscription_routes.SubscriptionService.get_subscription")
    def test_create_subscription_success(
        self,
        mock_get_subscription,
        mock_create_subscription,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/subscription for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_subscription.return_value = "123"
        mock_get_subscription.return_value = {
            "_id": "123",
            "name": "test-subscription",
            "status": "active",
        }

        response = self.client.post(
            "/api/subscription",
            json={"name": "test-subscription", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_subscription.assert_called_once()
        mock_get_subscription.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.subscription_routes.create_flask_token")
    @patch("src.routes.subscription_routes.create_flask_breadcrumb")
    @patch("src.routes.subscription_routes.SubscriptionService.get_subscriptions")
    def test_get_subscriptions_no_filter(
        self,
        mock_get_subscriptions,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/subscription without name filter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_subscriptions.return_value = {
            "items": [
                {"_id": "123", "name": "subscription1"},
                {"_id": "456", "name": "subscription2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/subscription")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_subscriptions.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.subscription_routes.create_flask_token")
    @patch("src.routes.subscription_routes.create_flask_breadcrumb")
    @patch("src.routes.subscription_routes.SubscriptionService.get_subscriptions")
    def test_get_subscriptions_with_name_filter(
        self,
        mock_get_subscriptions,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/subscription with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_subscriptions.return_value = {
            "items": [{"_id": "123", "name": "test-subscription"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/subscription?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_subscriptions.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.subscription_routes.create_flask_token")
    @patch("src.routes.subscription_routes.create_flask_breadcrumb")
    @patch("src.routes.subscription_routes.SubscriptionService.get_subscription")
    def test_get_subscription_success(
        self,
        mock_get_subscription,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/subscription/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_subscription.return_value = {
            "_id": "123",
            "name": "subscription1",
        }

        response = self.client.get("/api/subscription/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_subscription.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.subscription_routes.create_flask_token")
    @patch("src.routes.subscription_routes.create_flask_breadcrumb")
    @patch("src.routes.subscription_routes.SubscriptionService.get_subscription")
    def test_get_subscription_not_found(
        self,
        mock_get_subscription,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/subscription/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_subscription.side_effect = HTTPNotFound(
            "Subscription 999 not found"
        )

        response = self.client.get("/api/subscription/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Subscription 999 not found")

    @patch("src.routes.subscription_routes.create_flask_token")
    def test_create_subscription_unauthorized(self, mock_create_token):
        """Test POST /api/subscription when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/subscription",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
