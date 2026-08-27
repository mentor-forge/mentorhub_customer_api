"""
Journey service for business logic and RBAC.

Subclasses shared JourneyService from api_utils.
"""

from api_utils.services import JourneyService as SharedJourneyService


class JourneyService(SharedJourneyService):
    """
    Service class for Journey domain operations.
    """

    pass
