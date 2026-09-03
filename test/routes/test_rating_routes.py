"""
Unit tests for Rating routes (consume-style, read-only).
"""

import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.rating_routes import create_rating_routes


class TestRatingRoutes(unittest.TestCase):
    """Test cases for Rating routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_rating_routes(),
            url_prefix="/api/rating",
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

    @patch("src.routes.rating_routes.create_flask_token")
    @patch("src.routes.rating_routes.create_flask_breadcrumb")
    @patch("src.routes.rating_routes.RatingService.get_ratings")
    def test_get_ratings_success(
        self,
        mock_get_ratings,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/rating for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_ratings.return_value = [
            {"_id": "123", "name": "rating1"},
            {"_id": "456", "name": "rating2"},
        ]

        response = self.client.get("/api/rating")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        mock_get_ratings.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            offset=0,
            size=20,
            filters={},
            sort_by=[("name", 1), ("_id", 1)],
        )

    @patch("src.routes.rating_routes.create_flask_token")
    @patch("src.routes.rating_routes.create_flask_breadcrumb")
    @patch("src.routes.rating_routes.RatingService.get_ratings")
    def test_get_ratings_with_name_filter(
        self,
        mock_get_ratings,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/rating with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_ratings.return_value = [{"_id": "123", "name": "test-rating"}]

        response = self.client.get("/api/rating?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        mock_get_ratings.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            offset=0,
            size=20,
            filters={"name": "test"},
            sort_by=[("name", 1), ("_id", 1)],
        )

    @patch("src.routes.rating_routes.create_flask_token")
    @patch("src.routes.rating_routes.create_flask_breadcrumb")
    @patch("src.routes.rating_routes.RatingService.get_rating")
    def test_get_rating_success(
        self,
        mock_get_rating,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/rating/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_rating.return_value = {
            "_id": "123",
            "name": "rating1",
        }

        response = self.client.get("/api/rating/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["name"], "rating1")
        mock_get_rating.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )


if __name__ == "__main__":
    unittest.main()
