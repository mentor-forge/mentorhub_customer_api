"""
Customer routes for Flask API.

Provides endpoints for Customer domain:
- GET /api/customer - Get all customer documents
- GET /api/customer/<id> - Get a specific customer document by ID
"""

from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from api_utils.flask_utils.list_request import parse_list_request
from src.services.customer_service import (
    CustomerService,
    CUSTOMER_LIST_FILTERS,
    CUSTOMER_LIST_ORDER,
)

import logging

logger = logging.getLogger(__name__)


def create_customer_routes():
    """
    Create a Flask Blueprint exposing customer endpoints.

    Returns:
        Blueprint: Flask Blueprint with customer routes
    """
    customer_routes = Blueprint("customer_routes", __name__)

    @customer_routes.route("", methods=["GET"])
    @handle_route_exceptions
    def get_customers():
        """
        GET /api/customer - Retrieve paginated list of customer documents.
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)

        offset, size, filters, sort_by = parse_list_request(
            request, CUSTOMER_LIST_FILTERS, CUSTOMER_LIST_ORDER
        )

        result = CustomerService.get_customers(
            token,
            breadcrumb,
            offset=offset,
            size=size,
            filters=filters,
            sort_by=sort_by,
        )

        logger.info(
            f"get_customers Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}"
        )
        return jsonify(result), 200

    @customer_routes.route("/<customer_id>", methods=["GET"])
    @handle_route_exceptions
    def get_customer(customer_id):
        """
        GET /api/customer/<id> - Retrieve a specific customer document by ID.
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)

        customer = CustomerService.get_customer(customer_id, token, breadcrumb)
        logger.info(
            f"get_customer Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}"
        )
        return jsonify(customer), 200

    logger.info("Customer Flask Routes Registered")
    return customer_routes
