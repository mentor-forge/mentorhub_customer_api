"""
Rating routes for Flask API.

Provides endpoints for Rating domain:
- GET /api/rating - Get all rating documents
- GET /api/rating/<id> - Get a specific rating document by ID
"""

from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from api_utils.flask_utils.list_request import parse_list_request
from src.services.rating_service import (
    RatingService,
    RATING_LIST_FILTERS,
    RATING_LIST_ORDER,
)

import logging

logger = logging.getLogger(__name__)


def create_rating_routes():
    """
    Create a Flask Blueprint exposing rating endpoints.

    Returns:
        Blueprint: Flask Blueprint with rating routes
    """
    rating_routes = Blueprint("rating_routes", __name__)

    @rating_routes.route("", methods=["GET"])
    @handle_route_exceptions
    def get_ratings():
        """
        GET /api/rating - Retrieve paginated list of rating documents.
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)

        offset, size, filters, sort_by = parse_list_request(
            request, RATING_LIST_FILTERS, RATING_LIST_ORDER
        )

        result = RatingService.get_ratings(
            token,
            breadcrumb,
            offset=offset,
            size=size,
            filters=filters,
            sort_by=sort_by,
        )

        logger.info(
            f"get_ratings Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}"
        )
        return jsonify(result), 200

    @rating_routes.route("/<rating_id>", methods=["GET"])
    @handle_route_exceptions
    def get_rating(rating_id):
        """
        GET /api/rating/<id> - Retrieve a specific rating document by ID.
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)

        rating = RatingService.get_rating(rating_id, token, breadcrumb)
        logger.info(
            f"get_rating Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}"
        )
        return jsonify(rating), 200

    logger.info("Rating Flask Routes Registered")
    return rating_routes
