"""
Unit tests for Event routes.
"""

import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.event_routes import create_event_routes


class TestEventRoutes(unittest.TestCase):
    """Test cases for Event routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_event_routes(),
            url_prefix="/api/event",
        )
        self.client = self.app.test_client()

        self.mock_token = {
            "user_id": "test_user",
            "display_name": "Test User",
            "roles": ["developer"],
        }
        self.mock_breadcrumb = {
            "at_time": "sometime",
            "correlation_id": "correlation_ID",
        }

    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("src.services.event_service.EventService.get_events")
    def test_get_events_success(
        self,
        mock_get_events,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/event for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_events.return_value = [
            {"_id": "123", "type": "login"},
            {"_id": "456", "type": "logout"},
        ]

        response = self.client.get("/api/event")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        mock_get_events.assert_called_once()

    @patch("src.routes.event_routes.create_flask_token")
    @patch("src.routes.event_routes.create_flask_breadcrumb")
    @patch("src.services.event_service.EventService.create_event")
    def test_create_event_success(
        self,
        mock_create_event,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/event for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_event.return_value = {
            "_id": "123",
            "type": "login",
        }

        response = self.client.post("/api/event", json={"type": "login"})

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["type"], "login")
        mock_create_event.assert_called_once_with(
            {"type": "login"}, self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.event_routes.create_flask_token")
    @patch("src.routes.event_routes.create_flask_breadcrumb")
    @patch("src.services.event_service.EventService.get_event")
    def test_get_event_success(
        self,
        mock_get_event,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/event/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_event.return_value = {
            "_id": "123",
            "type": "login",
        }

        response = self.client.get("/api/event/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["type"], "login")
        mock_get_event.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )


if __name__ == "__main__":
    unittest.main()
