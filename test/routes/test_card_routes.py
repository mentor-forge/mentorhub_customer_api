"""
Unit tests for Card routes.

These tests validate the Flask route layer for the Card domain, using the
generated blueprint factory and mocking out the underlying service and
token/breadcrumb helpers from api_utils.
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.card_routes import create_card_routes


class TestCardRoutes(unittest.TestCase):
    """Test cases for Card routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_card_routes(),
            url_prefix="/api/card",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.card_routes.create_flask_token")
    @patch("src.routes.card_routes.create_flask_breadcrumb")
    @patch("src.routes.card_routes.CardService.create_card")
    @patch("src.routes.card_routes.CardService.get_card")
    def test_create_card_success(
        self,
        mock_get_card,
        mock_create_card,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/card for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_card.return_value = "123"
        mock_get_card.return_value = {
            "_id": "123",
            "name": "test-card",
            "status": "active",
        }

        response = self.client.post(
            "/api/card",
            json={"name": "test-card", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_card.assert_called_once()
        mock_get_card.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.card_routes.create_flask_token")
    @patch("src.routes.card_routes.create_flask_breadcrumb")
    @patch("src.routes.card_routes.CardService.get_cards")
    def test_get_cards_no_filter(
        self,
        mock_get_cards,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/card without name filter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_cards.return_value = {
            "items": [
                {"_id": "123", "name": "card1"},
                {"_id": "456", "name": "card2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/card")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_cards.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.card_routes.create_flask_token")
    @patch("src.routes.card_routes.create_flask_breadcrumb")
    @patch("src.routes.card_routes.CardService.get_cards")
    def test_get_cards_with_name_filter(
        self,
        mock_get_cards,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/card with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_cards.return_value = {
            "items": [{"_id": "123", "name": "test-card"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/card?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_cards.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.card_routes.create_flask_token")
    @patch("src.routes.card_routes.create_flask_breadcrumb")
    @patch("src.routes.card_routes.CardService.get_card")
    def test_get_card_success(
        self,
        mock_get_card,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/card/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_card.return_value = {
            "_id": "123",
            "name": "card1",
        }

        response = self.client.get("/api/card/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_card.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.card_routes.create_flask_token")
    @patch("src.routes.card_routes.create_flask_breadcrumb")
    @patch("src.routes.card_routes.CardService.get_card")
    def test_get_card_not_found(
        self,
        mock_get_card,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/card/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_card.side_effect = HTTPNotFound(
            "Card 999 not found"
        )

        response = self.client.get("/api/card/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Card 999 not found")

    @patch("src.routes.card_routes.create_flask_token")
    def test_create_card_unauthorized(self, mock_create_token):
        """Test POST /api/card when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/card",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
