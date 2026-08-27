"""
Note service for business logic and RBAC.

Subclasses shared NoteService from api_utils and provides get_note by-id.
"""

from api_utils.services import NoteService as SharedNoteService
from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import HTTPNotFound, HTTPInternalServerError
import logging

logger = logging.getLogger(__name__)


class NoteService(SharedNoteService):
    """
    Service class for Note domain operations.
    """

    @classmethod
    def get_note(cls, note_id, token, breadcrumb):
        """
        Retrieve a specific note document by ID.
        """
        try:
            cls._check_permission(token, "read")
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            note = mongo.get_document(config.NOTE_COLLECTION_NAME, note_id)
            if note is None:
                raise HTTPNotFound(f"Note {note_id} not found")

            logger.info(f"Retrieved note {note_id} for user {token.get('user_id')}")
            return note
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving note {note_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve note {note_id}")
