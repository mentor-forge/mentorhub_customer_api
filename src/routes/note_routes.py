"""
Note routes for Flask API.

Provides endpoints for Note domain:
- GET /api/note - Get paginated note documents for a resource (from shared factory)
- GET /api/note/<id> - Get a specific note document by ID
"""

from flask import jsonify
from api_utils.routes.shared_get_routes import create_note_get_routes
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.note_service import NoteService

import logging

logger = logging.getLogger(__name__)


def create_note_routes():
    """
    Create Flask Blueprint for Note routes.
    """
    bp = create_note_get_routes(NoteService)

    @bp.route("/<note_id>", methods=["GET"])
    @handle_route_exceptions
    def get_note(note_id):
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        note = NoteService.get_note(note_id, token, breadcrumb)
        logger.info(
            f"get_note Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}"
        )
        return jsonify(note), 200

    return bp
