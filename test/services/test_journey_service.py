"""
Unit tests for Journey service (read-only by-id).
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from src.services.journey_service import JourneyService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestJourneyService(unittest.TestCase):
    """Test cases for JourneyService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = {
            "user_id": "test_user",
            "display_name": "Test User",
            "roles": ["developer", "admin"],
            "profile_id": "507f1f77bcf86cd799439011",
        }
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_success(self, mock_get_mongo, mock_get_config):
        """Test successful retrieval of single journey."""
        mock_config = MagicMock()
        mock_config.JOURNEY_COLLECTION_NAME = "Journey"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "profile_id": ObjectId("507f1f77bcf86cd799439011"),
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey(
            "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(str(result["_id"]), "507f1f77bcf86cd799439011")

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_not_found(self, mock_get_mongo, mock_get_config):
        """Test retrieval of non-existent journey."""
        mock_config = MagicMock()
        mock_config.JOURNEY_COLLECTION_NAME = "Journey"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            JourneyService.get_journey(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )


if __name__ == "__main__":
    unittest.main()
