"""
Event service for business logic and RBAC.

Subclasses shared EventService from api_utils and provides get_event by-id.
"""

from api_utils.services import EventService as SharedEventService
from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import HTTPNotFound, HTTPInternalServerError
import logging

logger = logging.getLogger(__name__)


class EventService(SharedEventService):
    """
    Service class for Event domain operations.
    """

    @classmethod
    def get_event(cls, event_id, token, breadcrumb):
        """
        Retrieve a specific event document by ID.
        """
        try:
            cls._check_permission(token, "read")
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            event = mongo.get_document(config.EVENT_COLLECTION_NAME, event_id)
            if event is None:
                raise HTTPNotFound(f"Event {event_id} not found")

            logger.info(f"Retrieved event {event_id} for user {token.get('user_id')}")
            return event
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving event {event_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve event {event_id}")
