"""
Unit tests for Customer service (consume-style, read-only).
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from src.services.customer_service import CustomerService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestCustomerService(unittest.TestCase):
    """Test cases for CustomerService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = {"user_id": "test_user", "roles": ["developer"]}
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("src.services.customer_service.execute_list_query")
    @patch("src.services.customer_service.Config.get_instance")
    def test_get_customers_success(self, mock_get_config, mock_execute_list_query):
        """Test successful retrieval of customers."""
        mock_config = MagicMock()
        mock_config.CUSTOMER_COLLECTION_NAME = "Customer"
        mock_get_config.return_value = mock_config

        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "customer1"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "customer2"},
        ]
        mock_execute_list_query.return_value = mock_docs

        result = CustomerService.get_customers(
            self.mock_token, self.mock_breadcrumb, offset=0, size=20
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        mock_execute_list_query.assert_called_once_with(
            "Customer", match={}, sort_by=None, offset=0, size=20
        )

    @patch("src.services.customer_service.execute_list_query")
    @patch("src.services.customer_service.Config.get_instance")
    def test_get_customers_with_name_filter(
        self, mock_get_config, mock_execute_list_query
    ):
        """Test retrieval with filters."""
        mock_config = MagicMock()
        mock_config.CUSTOMER_COLLECTION_NAME = "Customer"
        mock_get_config.return_value = mock_config

        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "test-customer"}
        ]
        mock_execute_list_query.return_value = mock_docs

        result = CustomerService.get_customers(
            self.mock_token,
            self.mock_breadcrumb,
            filters={"name": "test"},
        )

        self.assertEqual(len(result), 1)
        mock_execute_list_query.assert_called_once()
        match_call = mock_execute_list_query.call_args[1]["match"]
        self.assertIn("name", match_call)

    @patch("src.services.customer_service.execute_list_query")
    @patch("src.services.customer_service.Config.get_instance")
    def test_get_customers_handles_exception(
        self, mock_get_config, mock_execute_list_query
    ):
        """Test handling of unexpected exceptions."""
        mock_config = MagicMock()
        mock_config.CUSTOMER_COLLECTION_NAME = "Customer"
        mock_get_config.return_value = mock_config
        mock_execute_list_query.side_effect = Exception("Database error")

        with self.assertRaises(HTTPInternalServerError):
            CustomerService.get_customers(self.mock_token, self.mock_breadcrumb)

    @patch("src.services.customer_service.Config.get_instance")
    @patch("src.services.customer_service.MongoIO.get_instance")
    def test_get_customer_success(self, mock_get_mongo, mock_get_config):
        """Test successful retrieval of single customer."""
        mock_config = MagicMock()
        mock_config.CUSTOMER_COLLECTION_NAME = "Customer"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "customer1",
        }
        mock_get_mongo.return_value = mock_mongo

        result = CustomerService.get_customer(
            "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["name"], "customer1")
        mock_mongo.get_document.assert_called_once_with(
            "Customer", "507f1f77bcf86cd799439011"
        )

    @patch("src.services.customer_service.Config.get_instance")
    @patch("src.services.customer_service.MongoIO.get_instance")
    def test_get_customer_not_found(self, mock_get_mongo, mock_get_config):
        """Test retrieval of non-existent customer."""
        mock_config = MagicMock()
        mock_config.CUSTOMER_COLLECTION_NAME = "Customer"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            CustomerService.get_customer(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )

    @patch("src.services.customer_service.Config.get_instance")
    @patch("src.services.customer_service.MongoIO.get_instance")
    def test_get_customer_handles_exception(self, mock_get_mongo, mock_get_config):
        """Test get_customer handling of unexpected exceptions."""
        mock_config = MagicMock()
        mock_config.CUSTOMER_COLLECTION_NAME = "Customer"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            CustomerService.get_customer(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )

    def test_check_permission_placeholder(self):
        """Test that _check_permission does not raise for valid token."""
        try:
            CustomerService._check_permission(self.mock_token, "read")
        except Exception as e:
            self.fail(f"_check_permission raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
