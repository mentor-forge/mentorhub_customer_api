"""
Profile service for business logic and RBAC.

Subclasses shared ProfileService from api_utils.
"""

from api_utils.services import ProfileService as SharedProfileService


class ProfileService(SharedProfileService):
    """
    Service class for Profile domain operations.
    """

    pass
