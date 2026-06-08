"""
Card routes for Flask API.

Provides endpoints for Card domain:
- POST /api/card - Create a new card document
- GET /api/card - Get all card documents (with optional ?name= query parameter)
- GET /api/card/<id> - Get a specific card document by ID
- PATCH /api/card/<id> - Update a card document
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.card_service import CardService

import logging
logger = logging.getLogger(__name__)


def create_card_routes():
    """
    Create a Flask Blueprint exposing card endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with card routes
    """
    card_routes = Blueprint('card_routes', __name__)
    
    @card_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_card():
        """
        POST /api/card - Create a new card document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the created card document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        card_id = CardService.create_card(data, token, breadcrumb)
        card = CardService.get_card(card_id, token, breadcrumb)
        
        logger.info(f"create_card Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(card), 201
    
    @card_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_cards():
        """
        GET /api/card - Retrieve infinite scroll batch of sorted, filtered card documents.
        
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
        result = CardService.get_cards(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_cards Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @card_routes.route('/<card_id>', methods=['GET'])
    @handle_route_exceptions
    def get_card(card_id):
        """
        GET /api/card/<id> - Retrieve a specific card document by ID.
        
        Args:
            card_id: The card ID to retrieve
            
        Returns:
            JSON response with the card document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        card = CardService.get_card(card_id, token, breadcrumb)
        logger.info(f"get_card Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(card), 200
    
    @card_routes.route('/<card_id>', methods=['PATCH'])
    @handle_route_exceptions
    def update_card(card_id):
        """
        PATCH /api/card/<id> - Update a card document.
        
        Args:
            card_id: The card ID to update
            
        Request body (JSON):
        {
            "name": "new_value",
            "description": "new_value",
            "status": "archived",
            ...
        }
        
        Returns:
            JSON response with the updated card document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        card = CardService.update_card(card_id, data, token, breadcrumb)
        
        logger.info(f"update_card Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(card), 200
    
    logger.info("Card Flask Routes Registered")
    return card_routes