"""
Unit tests for Journey routes (by-id only).
"""

import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.journey_routes import create_journey_routes


class TestJourneyRoutes(unittest.TestCase):
    """Test cases for Journey routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_journey_routes(),
            url_prefix="/api/journey",
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

    def test_get_journeys_list_not_found(self):
        """Test GET /api/journey collection returns 404 (by-id only)."""
        response = self.client.get("/api/journey")
        self.assertEqual(response.status_code, 404)

    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("src.services.journey_service.JourneyService.get_journey")
    def test_get_journey_success(
        self,
        mock_get_journey,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/journey/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_journey.return_value = {
            "_id": "123",
            "status": "active",
        }

        response = self.client.get("/api/journey/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["status"], "active")
        mock_get_journey.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )


if __name__ == "__main__":
    unittest.main()
