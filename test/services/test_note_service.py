"""
Unit tests for Note service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from src.services.note_service import NoteService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestNoteService(unittest.TestCase):
    """Test cases for NoteService."""

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

    @patch("api_utils.services.note_service.execute_list_query")
    @patch("api_utils.services.note_service.Config.get_instance")
    def test_get_notes_for_resource_success(
        self, mock_get_config, mock_execute_list_query
    ):
        """Test successful retrieval of notes for resource."""
        mock_config = MagicMock()
        mock_config.NOTE_COLLECTION_NAME = "Note"
        mock_get_config.return_value = mock_config

        mock_docs = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "resource_id": ObjectId("507f1f77bcf86cd799439012"),
                "note": "A note",
            }
        ]
        mock_execute_list_query.return_value = mock_docs

        result = NoteService.get_notes_for_resource(
            "507f1f77bcf86cd799439012",
            self.mock_token,
            self.mock_breadcrumb,
            offset=0,
            size=20,
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        mock_execute_list_query.assert_called_once()

    @patch("src.services.note_service.Config.get_instance")
    @patch("src.services.note_service.MongoIO.get_instance")
    def test_get_note_success(self, mock_get_mongo, mock_get_config):
        """Test successful retrieval of single note."""
        mock_config = MagicMock()
        mock_config.NOTE_COLLECTION_NAME = "Note"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "note": "A note",
        }
        mock_get_mongo.return_value = mock_mongo

        result = NoteService.get_note(
            "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["note"], "A note")

    @patch("src.services.note_service.Config.get_instance")
    @patch("src.services.note_service.MongoIO.get_instance")
    def test_get_note_not_found(self, mock_get_mongo, mock_get_config):
        """Test retrieval of non-existent note."""
        mock_config = MagicMock()
        mock_config.NOTE_COLLECTION_NAME = "Note"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            NoteService.get_note(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )

    @patch("src.services.note_service.Config.get_instance")
    @patch("src.services.note_service.MongoIO.get_instance")
    def test_get_note_handles_exception(self, mock_get_mongo, mock_get_config):
        """Test get_note handling of unexpected exceptions."""
        mock_config = MagicMock()
        mock_config.NOTE_COLLECTION_NAME = "Note"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            NoteService.get_note(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )


if __name__ == "__main__":
    unittest.main()
