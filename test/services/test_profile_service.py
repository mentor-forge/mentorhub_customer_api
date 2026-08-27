"""
Unit tests for Profile service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from src.services.profile_service import ProfileService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestProfileService(unittest.TestCase):
    """Test cases for ProfileService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = {
            "user_id": "test_user",
            "roles": ["developer", "admin"],
            "profile_id": "507f1f77bcf86cd799439011",
        }
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.profile_service.execute_list_query")
    @patch("api_utils.services.profile_service.Config.get_instance")
    def test_get_profiles_success(self, mock_get_config, mock_execute_list_query):
        """Test successful retrieval of profiles."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_get_config.return_value = mock_config

        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "profile1"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "profile2"},
        ]
        mock_execute_list_query.return_value = mock_docs

        result = ProfileService.get_profiles(
            self.mock_token, self.mock_breadcrumb, offset=0, size=20
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
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "profile1",
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        result = ProfileService.get_profile(
            "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["name"], "profile1")

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profile_not_found(self, mock_get_mongo, mock_get_config):
        """Test retrieval of non-existent profile."""
        mock_config = MagicMock()
        mock_config.PROFILE_COLLECTION_NAME = "Profile"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            ProfileService.get_profile(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )


if __name__ == "__main__":
    unittest.main()
