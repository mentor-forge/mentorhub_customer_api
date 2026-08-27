"""
Unit tests for Customer routes (consume-style, read-only).
"""

import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.customer_routes import create_customer_routes


class TestCustomerRoutes(unittest.TestCase):
    """Test cases for Customer routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_customer_routes(),
            url_prefix="/api/customer",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["developer"]}
        self.mock_breadcrumb = {
            "at_time": "sometime",
            "correlation_id": "correlation_ID",
        }

    @patch("src.routes.customer_routes.create_flask_token")
    @patch("src.routes.customer_routes.create_flask_breadcrumb")
    @patch("src.routes.customer_routes.CustomerService.get_customers")
    def test_get_customers_success(
        self,
        mock_get_customers,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/customer for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_customers.return_value = [
            {"_id": "123", "name": "customer1"},
            {"_id": "456", "name": "customer2"},
        ]

        response = self.client.get("/api/customer")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        mock_get_customers.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            offset=0,
            size=20,
            filters={},
            sort_by=[("name", 1), ("_id", 1)],
        )

    @patch("src.routes.customer_routes.create_flask_token")
    @patch("src.routes.customer_routes.create_flask_breadcrumb")
    @patch("src.routes.customer_routes.CustomerService.get_customers")
    def test_get_customers_with_name_filter(
        self,
        mock_get_customers,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/customer with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_customers.return_value = [{"_id": "123", "name": "test-customer"}]

        response = self.client.get("/api/customer?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        mock_get_customers.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            offset=0,
            size=20,
            filters={"name": "test"},
            sort_by=[("name", 1), ("_id", 1)],
        )

    @patch("src.routes.customer_routes.create_flask_token")
    @patch("src.routes.customer_routes.create_flask_breadcrumb")
    @patch("src.routes.customer_routes.CustomerService.get_customer")
    def test_get_customer_success(
        self,
        mock_get_customer,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/customer/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_customer.return_value = {
            "_id": "123",
            "name": "customer1",
        }

        response = self.client.get("/api/customer/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["name"], "customer1")
        mock_get_customer.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )


if __name__ == "__main__":
    unittest.main()
