"""
Journey routes for Flask API.
"""

from api_utils.routes.shared_get_routes import create_journey_get_routes
from src.services.journey_service import JourneyService


def create_journey_routes():
    """
    Create Flask Blueprint for Journey routes using shared factory.
    """
    return create_journey_get_routes(JourneyService)
