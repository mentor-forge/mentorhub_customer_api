"""
Profile routes for Flask API.

Provides endpoints for Profile domain:
- GET /api/profile - Get paginated profile documents (shared factory)
- POST /api/profile - Create a new profile document
- GET /api/profile/<id> - Get a specific profile document by ID (shared factory)
- PATCH /api/profile/<id> - Update an existing profile document
"""

from flask import jsonify, request
from api_utils.routes.shared_get_routes import create_profile_get_routes
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.profile_service import ProfileService

import logging

logger = logging.getLogger(__name__)


def create_profile_routes():
    """
    Create Flask Blueprint for Profile routes.
    """
    bp = create_profile_get_routes(ProfileService)

    @bp.route("", methods=["POST"])
    @handle_route_exceptions
    def create_profile():
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        data = request.get_json() or {}
        profile = ProfileService.create_profile(data, token, breadcrumb)
        logger.info(
            f"create_profile Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}"
        )
        return jsonify(profile), 201

    @bp.route("/<profile_id>", methods=["PATCH"])
    @handle_route_exceptions
    def update_profile(profile_id):
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        data = request.get_json() or {}
        profile = ProfileService.update_profile(profile_id, data, token, breadcrumb)
        logger.info(
            f"update_profile Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}"
        )
        return jsonify(profile), 200

    return bp
