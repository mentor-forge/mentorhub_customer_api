"""
Journey routes for Flask API.

Provides endpoints for Journey domain:
- GET /api/journey - Get all journey documents
- GET /api/journey/<id> - Get a specific journey document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.journey_service import JourneyService

import logging
logger = logging.getLogger(__name__)


def create_journey_routes():
    """
    Create a Flask Blueprint exposing journey endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with journey routes
    """
    journey_routes = Blueprint('journey_routes', __name__)
    
    @journey_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_journeys():
        """
        GET /api/journey - Retrieve infinite scroll batch of sorted, filtered journey documents.
        
        Query Parameters:
            name: Optional name filter
            after_id: Cursor for infinite scroll (ID of last item from previous batch, omit for first request)
            limit: Items per batch (default: 10, max: 100)
            sort_by: Field to sort by (default: 'name')
            order: Sort order 'asc' or 'desc' (default: 'asc')
        
        Returns:
            JSON response with infinite scroll results: {
                'items': [...],
                'limit': int,
                'has_more': bool,
                'next_cursor': str|None
            }
        
        Raises:
            400 Bad Request: If invalid parameters provided
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        # Get query parameters
        name = request.args.get('name')
        after_id = request.args.get('after_id')
        limit = request.args.get('limit', 10, type=int)
        sort_by = request.args.get('sort_by', 'name')
        order = request.args.get('order', 'asc')
        
        # Service layer validates parameters and raises HTTPBadRequest if invalid
        # @handle_route_exceptions decorator will catch and format the exception
        result = JourneyService.get_journeys(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_journeys Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @journey_routes.route('/<journey_id>', methods=['GET'])
    @handle_route_exceptions
    def get_journey(journey_id):
        """
        GET /api/journey/<id> - Retrieve a specific journey document by ID.
        
        Args:
            journey_id: The journey ID to retrieve
            
        Returns:
            JSON response with the journey document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        journey = JourneyService.get_journey(journey_id, token, breadcrumb)
        logger.info(f"get_journey Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(journey), 200
    
    logger.info("Journey Flask Routes Registered")
    return journey_routes