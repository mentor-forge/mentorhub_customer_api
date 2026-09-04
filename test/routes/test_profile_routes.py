"""
Unit tests for Profile routes.
"""

import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.profile_routes import create_profile_routes


class TestProfileRoutes(unittest.TestCase):
    """Test cases for Profile routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_profile_routes(),
            url_prefix="/api/profile",
        )
        self.client = self.app.test_client()

        self.mock_token = {
            "user_id": "test_user",
            "display_name": "Test User",
            "roles": ["developer", "customer"],
        }
        self.mock_breadcrumb = {
            "at_time": "sometime",
            "correlation_id": "correlation_ID",
        }

    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("src.services.profile_service.ProfileService.get_profiles")
    def test_get_profiles_success(
        self,
        mock_get_profiles,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/profile for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_profiles.return_value = [
            {"_id": "123", "display_name": "Profile One"},
            {"_id": "456", "display_name": "Profile Two"},
        ]

        response = self.client.get("/api/profile")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        mock_get_profiles.assert_called_once()

    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("src.services.profile_service.ProfileService.get_profile")
    def test_get_profile_success(
        self,
        mock_get_profile,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/profile/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_profile.return_value = {
            "_id": "123",
            "display_name": "Profile One",
        }

        response = self.client.get("/api/profile/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["display_name"], "Profile One")
        mock_get_profile.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.profile_routes.create_flask_token")
    @patch("src.routes.profile_routes.create_flask_breadcrumb")
    @patch("src.routes.profile_routes.ProfileService.create_profile")
    def test_create_profile_success(
        self,
        mock_create_profile,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/profile for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_profile.return_value = {
            "_id": "123",
            "display_name": "New Profile",
        }

        response = self.client.post(
            "/api/profile", json={"display_name": "New Profile"}
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["display_name"], "New Profile")
        mock_create_profile.assert_called_once_with(
            {"display_name": "New Profile"}, self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.profile_routes.create_flask_token")
    @patch("src.routes.profile_routes.create_flask_breadcrumb")
    @patch("src.routes.profile_routes.ProfileService.update_profile")
    def test_update_profile_success(
        self,
        mock_update_profile,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test PATCH /api/profile/<id> for successful update."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_update_profile.return_value = {
            "_id": "123",
            "display_name": "Updated Profile",
            "description": "updated",
        }

        response = self.client.patch(
            "/api/profile/123", json={"description": "updated"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["description"], "updated")
        mock_update_profile.assert_called_once_with(
            "123", {"description": "updated"}, self.mock_token, self.mock_breadcrumb
        )


if __name__ == "__main__":
    unittest.main()
