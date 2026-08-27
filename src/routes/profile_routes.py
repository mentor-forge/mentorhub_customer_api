"""
Profile routes for Flask API.
"""

from api_utils.routes.shared_get_routes import create_profile_get_routes
from src.services.profile_service import ProfileService


def create_profile_routes():
    """
    Create Flask Blueprint for Profile routes using shared factory.
    """
    return create_profile_get_routes(ProfileService)
