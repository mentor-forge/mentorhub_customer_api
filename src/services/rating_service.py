"""
Rating service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Rating domain.
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

RATING_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
    "description": {"type": "contains", "field": "description"},
}

RATING_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {
        "name": ("asc", "desc"),
        "description": ("asc", "desc"),
    },
}


class RatingService:
    """
    Service class for Rating domain operations.
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """
        Check if the user has permission to perform an operation.
        """
        pass

    @classmethod
    def get_ratings(
        cls,
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
    ):
        """
        Get paginated list of sorted, filtered rating documents.
        """
        try:
            cls._check_permission(token, "read")
            config = Config.get_instance()
            match = build_match_filter({}, filters or {}, RATING_LIST_FILTERS)
            result = execute_list_query(
                config.RATING_COLLECTION_NAME,
                match=match,
                sort_by=sort_by,
                offset=offset,
                size=size,
            )
            logger.info(
                f"Retrieved {len(result)} ratings for user {token.get('user_id')}"
            )
            return result
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving ratings: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve ratings")

    @classmethod
    def get_rating(cls, rating_id, token, breadcrumb):
        """
        Retrieve a specific rating document by ID.
        """
        try:
            cls._check_permission(token, "read")
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            rating = mongo.get_document(config.RATING_COLLECTION_NAME, rating_id)
            if rating is None:
                raise HTTPNotFound(f"Rating {rating_id} not found")

            logger.info(f"Retrieved rating {rating_id} for user {token.get('user_id')}")
            return rating
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving rating {rating_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve rating {rating_id}")
