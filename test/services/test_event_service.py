"""
Unit tests for Event service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from src.services.event_service import EventService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestEventService(unittest.TestCase):
    """Test cases for EventService."""

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

    @patch("api_utils.services.event_service.execute_list_query")
    @patch("api_utils.services.event_service.Config.get_instance")
    def test_get_events_success(self, mock_get_config, mock_execute_list_query):
        """Test successful retrieval of events."""
        mock_config = MagicMock()
        mock_config.EVENT_COLLECTION_NAME = "Event"
        mock_get_config.return_value = mock_config

        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "type": "login"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "type": "logout"},
        ]
        mock_execute_list_query.return_value = mock_docs

        result = EventService.get_events(
            self.mock_token, self.mock_breadcrumb, offset=0, size=20
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        mock_execute_list_query.assert_called_once()

    @patch("api_utils.services.event_service.Config.get_instance")
    @patch("api_utils.services.event_service.MongoIO.get_instance")
    def test_create_event_success(self, mock_get_mongo, mock_get_config):
        """Test successful creation of event."""
        mock_config = MagicMock()
        mock_config.EVENT_COLLECTION_NAME = "Event"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = "507f1f77bcf86cd799439011"
        mock_get_mongo.return_value = mock_mongo

        result = EventService.create_event(
            {"type": "login"}, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["type"], "login")
        self.assertIn("created", result)
        self.assertIn("_id", result)
        self.assertEqual(result["context"]["display_name"], "Test User")
        self.assertNotIn("name", result["context"])

    @patch("src.services.event_service.Config.get_instance")
    @patch("src.services.event_service.MongoIO.get_instance")
    def test_get_event_success(self, mock_get_mongo, mock_get_config):
        """Test successful retrieval of single event."""
        mock_config = MagicMock()
        mock_config.EVENT_COLLECTION_NAME = "Event"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "type": "login",
        }
        mock_get_mongo.return_value = mock_mongo

        result = EventService.get_event(
            "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["type"], "login")

    @patch("src.services.event_service.Config.get_instance")
    @patch("src.services.event_service.MongoIO.get_instance")
    def test_get_event_not_found(self, mock_get_mongo, mock_get_config):
        """Test retrieval of non-existent event."""
        mock_config = MagicMock()
        mock_config.EVENT_COLLECTION_NAME = "Event"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            EventService.get_event(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )

    @patch("src.services.event_service.Config.get_instance")
    @patch("src.services.event_service.MongoIO.get_instance")
    def test_get_event_handles_exception(self, mock_get_mongo, mock_get_config):
        """Test get_event handling of unexpected exceptions."""
        mock_config = MagicMock()
        mock_config.EVENT_COLLECTION_NAME = "Event"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            EventService.get_event(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )


if __name__ == "__main__":
    unittest.main()
