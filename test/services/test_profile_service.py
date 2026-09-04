"""
Unit tests for Profile service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from src.services.profile_service import ProfileService
from api_utils.flask_utils.exceptions import (
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestProfileService(unittest.TestCase):
    """Test cases for ProfileService."""

    def setUp(self):
        """Set up the test fixture."""
        self.admin_token = {
            "user_id": "admin_user",
            "display_name": "Admin User",
            "roles": ["admin"],
            "profile_id": "507f1f77bcf86cd799439011",
        }
        self.customer_token = {
            "user_id": "customer_user",
            "display_name": "Customer User",
            "roles": ["customer"],
            "customer_id": "507f1f77bcf86cd799439099",
            "profile_id": "507f1f77bcf86cd799439011",
        }
        self.mentee_token = {
            "user_id": "mentee_user",
            "display_name": "Mentee User",
            "roles": ["mentee"],
            "profile_id": "507f1f77bcf86cd799439011",
        }
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("src.services.profile_service.execute_list_query")
    @patch("src.services.profile_service.Config.get_instance")
    def test_get_profiles_success(self, mock_get_config, mock_execute_list_query):
        """Test successful retrieval of profiles."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_docs = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "display_name": "Profile One",
            },
            {
                "_id": ObjectId("507f1f77bcf86cd799439012"),
                "display_name": "Profile Two",
            },
        ]
        mock_execute_list_query.return_value = mock_docs

        result = ProfileService.get_profiles(
            self.mentee_token, self.mock_breadcrumb, offset=0, size=20
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        mock_execute_list_query.assert_called_once()

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profile_success(self, mock_get_mongo, mock_get_config):
        """Test successful retrieval of single profile."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "display_name": "Profile One",
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        result = ProfileService.get_profile(
            "507f1f77bcf86cd799439011", self.admin_token, self.mock_breadcrumb
        )

        self.assertEqual(result["display_name"], "Profile One")

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profile_not_found(self, mock_get_mongo, mock_get_config):
        """Test retrieval of non-existent profile."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            ProfileService.get_profile(
                "507f1f77bcf86cd799439011", self.admin_token, self.mock_breadcrumb
            )

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_create_profile_as_customer_stamps_customer_id(
        self, mock_get_mongo, mock_get_config
    ):
        """Test customer create stamps customer_id from token."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_CUSTOMER = "customer"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = "507f1f77bcf86cd799439011"
        mock_get_mongo.return_value = mock_mongo

        data = {"display_name": "New User", "email": "new@example.com"}
        result = ProfileService.create_profile(
            data, self.customer_token, self.mock_breadcrumb
        )

        self.assertEqual(result["display_name"], "New User")
        self.assertEqual(result["customer_id"], ObjectId("507f1f77bcf86cd799439099"))
        self.assertIn("created", result)
        self.assertIn("saved", result)

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_create_profile_as_admin_allows_custom_customer_id(
        self, mock_get_mongo, mock_get_config
    ):
        """Test admin create does not force token customer_id."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_CUSTOMER = "customer"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = "507f1f77bcf86cd799439011"
        mock_get_mongo.return_value = mock_mongo

        data = {
            "display_name": "New User",
            "customer_id": "507f1f77bcf86cd799439088",
        }
        result = ProfileService.create_profile(
            data, self.admin_token, self.mock_breadcrumb
        )

        self.assertEqual(result["customer_id"], ObjectId("507f1f77bcf86cd799439088"))

    def test_create_profile_forbidden_for_non_customer(self):
        """Test create raises HTTPForbidden for non-customer non-admin."""
        with self.assertRaises(HTTPForbidden):
            ProfileService.create_profile(
                {"display_name": "Test"}, self.mentee_token, self.mock_breadcrumb
            )

    @patch("src.services.profile_service.Config.get_instance")
    @patch("src.services.profile_service.MongoIO.get_instance")
    def test_update_profile_as_admin_success(self, mock_get_mongo, mock_get_config):
        """Test admin can update any profile."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_ADMIN = "admin"
        mock_config.ROLE_CUSTOMER = "customer"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "display_name": "Target User",
            "customer_id": ObjectId("507f1f77bcf86cd799439088"),
        }
        mock_get_mongo.return_value = mock_mongo

        result = ProfileService.update_profile(
            "507f1f77bcf86cd799439011",
            {"description": "Updated by admin"},
            self.admin_token,
            self.mock_breadcrumb,
        )

        mock_mongo.update_document.assert_called_once()
        self.assertIsNotNone(result)

    @patch("src.services.profile_service.Config.get_instance")
    @patch("src.services.profile_service.MongoIO.get_instance")
    def test_update_profile_own_profile_success(self, mock_get_mongo, mock_get_config):
        """Test customer can update own profile."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_ADMIN = "admin"
        mock_config.ROLE_CUSTOMER = "customer"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "display_name": "Customer User",
            "customer_id": ObjectId("507f1f77bcf86cd799439099"),
        }
        mock_get_mongo.return_value = mock_mongo

        result = ProfileService.update_profile(
            "507f1f77bcf86cd799439011",
            {"description": "Self update"},
            self.customer_token,
            self.mock_breadcrumb,
        )

        mock_mongo.update_document.assert_called_once()
        self.assertIsNotNone(result)

    @patch("src.services.profile_service.Config.get_instance")
    @patch("src.services.profile_service.MongoIO.get_instance")
    def test_update_profile_same_customer_success(
        self, mock_get_mongo, mock_get_config
    ):
        """Test customer can update profile with matching customer_id."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_ADMIN = "admin"
        mock_config.ROLE_CUSTOMER = "customer"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439022"),
            "display_name": "Other User",
            "customer_id": ObjectId("507f1f77bcf86cd799439099"),
        }
        mock_get_mongo.return_value = mock_mongo

        result = ProfileService.update_profile(
            "507f1f77bcf86cd799439022",
            {"description": "Org update"},
            self.customer_token,
            self.mock_breadcrumb,
        )

        mock_mongo.update_document.assert_called_once()
        self.assertIsNotNone(result)

    @patch("src.services.profile_service.Config.get_instance")
    @patch("src.services.profile_service.MongoIO.get_instance")
    def test_update_profile_forbidden_different_customer(
        self, mock_get_mongo, mock_get_config
    ):
        """Test customer cannot update profile of different customer."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_ADMIN = "admin"
        mock_config.ROLE_CUSTOMER = "customer"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439022"),
            "display_name": "Other User",
            "customer_id": ObjectId("507f1f77bcf86cd799439088"),
        }
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPForbidden):
            ProfileService.update_profile(
                "507f1f77bcf86cd799439022",
                {"description": "Unauthorized update"},
                self.customer_token,
                self.mock_breadcrumb,
            )

    @patch("src.services.profile_service.Config.get_instance")
    @patch("src.services.profile_service.MongoIO.get_instance")
    def test_update_profile_strips_system_fields(self, mock_get_mongo, mock_get_config):
        """Test update strips _id, created, saved fields and stamps saved."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_config.ROLE_ADMIN = "admin"
        mock_config.ROLE_CUSTOMER = "customer"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "display_name": "Customer User",
            "customer_id": ObjectId("507f1f77bcf86cd799439099"),
        }
        mock_get_mongo.return_value = mock_mongo

        update_payload = {
            "_id": "attempted_id_change",
            "created": {"fake": "created"},
            "description": "Clean update",
        }

        ProfileService.update_profile(
            "507f1f77bcf86cd799439011",
            update_payload,
            self.customer_token,
            self.mock_breadcrumb,
        )

        update_call_kwargs = mock_mongo.update_document.call_args.kwargs
        updated_data = update_call_kwargs["set_data"]
        self.assertNotIn("_id", updated_data)
        self.assertNotIn("created", updated_data)
        self.assertEqual(updated_data["saved"], self.mock_breadcrumb)


if __name__ == "__main__":
    unittest.main()
