"""
Unit tests for Rating service (consume-style, read-only).
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from src.services.rating_service import RatingService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestRatingService(unittest.TestCase):
    """Test cases for RatingService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = {
            "user_id": "test_user",
            "display_name": "Test User",
            "roles": ["developer"],
        }
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("src.services.rating_service.execute_list_query")
    @patch("src.services.rating_service.Config.get_instance")
    def test_get_ratings_success(self, mock_get_config, mock_execute_list_query):
        """Test successful retrieval of ratings."""
        mock_config = MagicMock()
        mock_config.RATING_COLLECTION_NAME = "Rating"
        mock_get_config.return_value = mock_config

        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "rating1"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "rating2"},
        ]
        mock_execute_list_query.return_value = mock_docs

        result = RatingService.get_ratings(
            self.mock_token, self.mock_breadcrumb, offset=0, size=20
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        mock_execute_list_query.assert_called_once_with(
            "Rating", match={}, sort_by=None, offset=0, size=20
        )

    @patch("src.services.rating_service.execute_list_query")
    @patch("src.services.rating_service.Config.get_instance")
    def test_get_ratings_with_name_filter(
        self, mock_get_config, mock_execute_list_query
    ):
        """Test retrieval with filters."""
        mock_config = MagicMock()
        mock_config.RATING_COLLECTION_NAME = "Rating"
        mock_get_config.return_value = mock_config

        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "test-rating"}
        ]
        mock_execute_list_query.return_value = mock_docs

        result = RatingService.get_ratings(
            self.mock_token,
            self.mock_breadcrumb,
            filters={"name": "test"},
        )

        self.assertEqual(len(result), 1)
        mock_execute_list_query.assert_called_once()
        match_call = mock_execute_list_query.call_args[1]["match"]
        self.assertIn("name", match_call)

    @patch("src.services.rating_service.execute_list_query")
    @patch("src.services.rating_service.Config.get_instance")
    def test_get_ratings_handles_exception(
        self, mock_get_config, mock_execute_list_query
    ):
        """Test handling of unexpected exceptions."""
        mock_config = MagicMock()
        mock_config.RATING_COLLECTION_NAME = "Rating"
        mock_get_config.return_value = mock_config
        mock_execute_list_query.side_effect = Exception("Database error")

        with self.assertRaises(HTTPInternalServerError):
            RatingService.get_ratings(self.mock_token, self.mock_breadcrumb)

    @patch("src.services.rating_service.Config.get_instance")
    @patch("src.services.rating_service.MongoIO.get_instance")
    def test_get_rating_success(self, mock_get_mongo, mock_get_config):
        """Test successful retrieval of single rating."""
        mock_config = MagicMock()
        mock_config.RATING_COLLECTION_NAME = "Rating"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "rating1",
        }
        mock_get_mongo.return_value = mock_mongo

        result = RatingService.get_rating(
            "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["name"], "rating1")
        mock_mongo.get_document.assert_called_once_with(
            "Rating", "507f1f77bcf86cd799439011"
        )

    @patch("src.services.rating_service.Config.get_instance")
    @patch("src.services.rating_service.MongoIO.get_instance")
    def test_get_rating_not_found(self, mock_get_mongo, mock_get_config):
        """Test retrieval of non-existent rating."""
        mock_config = MagicMock()
        mock_config.RATING_COLLECTION_NAME = "Rating"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            RatingService.get_rating(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )

    @patch("src.services.rating_service.Config.get_instance")
    @patch("src.services.rating_service.MongoIO.get_instance")
    def test_get_rating_handles_exception(self, mock_get_mongo, mock_get_config):
        """Test get_rating handling of unexpected exceptions."""
        mock_config = MagicMock()
        mock_config.RATING_COLLECTION_NAME = "Rating"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            RatingService.get_rating(
                "507f1f77bcf86cd799439011", self.mock_token, self.mock_breadcrumb
            )

    def test_check_permission_placeholder(self):
        """Test that _check_permission does not raise for valid token."""
        try:
            RatingService._check_permission(self.mock_token, "read")
        except Exception as e:
            self.fail(f"_check_permission raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
