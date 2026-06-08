"""
Subscription routes for Flask API.

Provides endpoints for Subscription domain:
- POST /api/subscription - Create a new subscription document
- GET /api/subscription - Get all subscription documents (with optional ?name= query parameter)
- GET /api/subscription/<id> - Get a specific subscription document by ID
- PATCH /api/subscription/<id> - Update a subscription document
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.subscription_service import SubscriptionService

import logging
logger = logging.getLogger(__name__)


def create_subscription_routes():
    """
    Create a Flask Blueprint exposing subscription endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with subscription routes
    """
    subscription_routes = Blueprint('subscription_routes', __name__)
    
    @subscription_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_subscription():
        """
        POST /api/subscription - Create a new subscription document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the created subscription document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        subscription_id = SubscriptionService.create_subscription(data, token, breadcrumb)
        subscription = SubscriptionService.get_subscription(subscription_id, token, breadcrumb)
        
        logger.info(f"create_subscription Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(subscription), 201
    
    @subscription_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_subscriptions():
        """
        GET /api/subscription - Retrieve infinite scroll batch of sorted, filtered subscription documents.
        
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
        result = SubscriptionService.get_subscriptions(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_subscriptions Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @subscription_routes.route('/<subscription_id>', methods=['GET'])
    @handle_route_exceptions
    def get_subscription(subscription_id):
        """
        GET /api/subscription/<id> - Retrieve a specific subscription document by ID.
        
        Args:
            subscription_id: The subscription ID to retrieve
            
        Returns:
            JSON response with the subscription document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        subscription = SubscriptionService.get_subscription(subscription_id, token, breadcrumb)
        logger.info(f"get_subscription Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(subscription), 200
    
    @subscription_routes.route('/<subscription_id>', methods=['PATCH'])
    @handle_route_exceptions
    def update_subscription(subscription_id):
        """
        PATCH /api/subscription/<id> - Update a subscription document.
        
        Args:
            subscription_id: The subscription ID to update
            
        Request body (JSON):
        {
            "name": "new_value",
            "description": "new_value",
            "status": "archived",
            ...
        }
        
        Returns:
            JSON response with the updated subscription document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        subscription = SubscriptionService.update_subscription(subscription_id, data, token, breadcrumb)
        
        logger.info(f"update_subscription Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(subscription), 200
    
    logger.info("Subscription Flask Routes Registered")
    return subscription_routes