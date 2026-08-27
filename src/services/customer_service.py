"""
Customer service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Customer domain.
"""

from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)
from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    build_match_filter,
    execute_list_query,
)
import logging

logger = logging.getLogger(__name__)

CUSTOMER_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
    "description": {"type": "contains", "field": "description"},
}

CUSTOMER_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {
        "name": ("asc", "desc"),
        "description": ("asc", "desc"),
    },
}


class CustomerService:
    """
    Service class for Customer domain operations.
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """
        Check if the user has permission to perform an operation.
        """
        pass

    @classmethod
    def get_customers(
        cls,
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
    ):
        """
        Get paginated list of sorted, filtered customer documents.
        """
        try:
            cls._check_permission(token, "read")
            config = Config.get_instance()
            match = build_match_filter({}, filters or {}, CUSTOMER_LIST_FILTERS)
            result = execute_list_query(
                config.CUSTOMER_COLLECTION_NAME,
                match=match,
                sort_by=sort_by,
                offset=offset,
                size=size,
            )
            logger.info(
                f"Retrieved {len(result)} customers for user {token.get('user_id')}"
            )
            return result
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving customers: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve customers")

    @classmethod
    def get_customer(cls, customer_id, token, breadcrumb):
        """
        Retrieve a specific customer document by ID.
        """
        try:
            cls._check_permission(token, "read")
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            customer = mongo.get_document(config.CUSTOMER_COLLECTION_NAME, customer_id)
            if customer is None:
                raise HTTPNotFound(f"Customer {customer_id} not found")

            logger.info(
                f"Retrieved customer {customer_id} for user {token.get('user_id')}"
            )
            return customer
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving customer {customer_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve customer {customer_id}")
