"""
Unit tests for Note routes.
"""

import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.note_routes import create_note_routes


class TestNoteRoutes(unittest.TestCase):
    """Test cases for Note routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_note_routes(),
            url_prefix="/api/note",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["developer"]}
        self.mock_breadcrumb = {
            "at_time": "sometime",
            "correlation_id": "correlation_ID",
        }

    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("src.services.note_service.NoteService.get_notes_for_resource")
    def test_get_notes_success(
        self,
        mock_get_notes,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/note with resource_id for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_notes.return_value = [
            {"_id": "123", "note": "note1"},
            {"_id": "456", "note": "note2"},
        ]

        response = self.client.get("/api/note?resource_id=507f1f77bcf86cd799439011")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        mock_get_notes.assert_called_once()

    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    def test_get_notes_missing_resource_id(
        self,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/note without resource_id returns 400."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        response = self.client.get("/api/note")
        self.assertEqual(response.status_code, 400)

    @patch("src.routes.note_routes.create_flask_token")
    @patch("src.routes.note_routes.create_flask_breadcrumb")
    @patch("src.services.note_service.NoteService.get_note")
    def test_get_note_success(
        self,
        mock_get_note,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/note/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_note.return_value = {
            "_id": "123",
            "note": "note1",
        }

        response = self.client.get("/api/note/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["note"], "note1")
        mock_get_note.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )


if __name__ == "__main__":
    unittest.main()
