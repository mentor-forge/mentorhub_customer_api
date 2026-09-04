"""
Profile service for business logic and RBAC.

Customer controls Profile: provides inbound RBAC for create/update,
stamps customer_id on customer creation, and implements update_profile.
"""

import logging
from api_utils import Config, MongoIO
from api_utils.flask_utils.exceptions import (
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)
from api_utils.mongo_utils import encode_document
from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    build_match_filter,
    build_sort_by,
    execute_list_query,
)
from api_utils.services import ProfileService as SharedProfileService
from api_utils.services.profile_service import (
    ID_PROPERTIES,
    DATE_PROPERTIES,
    SYSTEM_MANAGED_FIELDS,
)
from api_utils.services.rbac import is_admin

logger = logging.getLogger(__name__)

PROFILE_LIST_FILTERS = {
    "display_name": {"type": "contains", "field": "display_name"},
    "email": {"type": "contains", "field": "email"},
    "description": {"type": "contains", "field": "description"},
    "status": {"type": "in_list", "field": "status"},
    "roles": {"type": "in_list", "field": "roles"},
}
PROFILE_LIST_ORDER = {
    "default": {"field": "display_name", "order": "asc"},
    "allowed": {
        "display_name": ("asc", "desc"),
        "email": ("asc", "desc"),
        "status": ("asc", "desc"),
        "created.at_time": ("asc", "desc"),
        "saved.at_time": ("asc", "desc"),
    },
}


class ProfileService(SharedProfileService):
    """
    Service class for Profile domain operations (Customer control).
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """
        Check if user has permission to perform operation.
        Writes (create/update) require customer or admin role.
        Reads allow any authenticated user (outbound scoping handles visibility).
        """
        if operation in ("create", "update"):
            config = Config.get_instance()
            roles = token.get("roles", []) if token else []
            if not (
                is_admin(token)
                or config.ROLE_CUSTOMER in roles
                or "customer" in roles
                or "admin" in roles
            ):
                raise HTTPForbidden(
                    "Only customers and administrators may perform this action"
                )
        else:
            super()._check_permission(token, operation)

    @classmethod
    def create_profile(cls, data, token, breadcrumb):
        """
        Create a new profile document.
        Stamps customer_id from token if caller is a customer (not admin).
        """
        cls._check_permission(token, "create")

        if not is_admin(token) and "customer_id" in token:
            data["customer_id"] = token["customer_id"]

        return super().create_profile(data, token, breadcrumb)

    @classmethod
    def get_profiles(
        cls,
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
    ):
        """List Profiles using the current ``display_name`` schema."""
        cls._check_permission(token, "read")

        match = build_match_filter(
            cls._outbound_match(token), filters or {}, PROFILE_LIST_FILTERS
        )
        if sort_by is None:
            default = PROFILE_LIST_ORDER["default"]
            sort_by = build_sort_by(
                default["field"], default["order"], PROFILE_LIST_ORDER
            )

        config = Config.get_instance()
        profiles = execute_list_query(
            config.PROFILE_COLLECTION_NAME,
            match=match,
            sort_by=sort_by,
            offset=offset,
            size=size,
        )
        logger.info(
            f"Retrieved {len(profiles)} profiles (offset={offset}, size={size}) "
            f"for user {token.get('user_id')}"
        )
        return profiles

    @classmethod
    def update_profile(cls, profile_id, data, token, breadcrumb):
        """
        Update an existing profile document.

        Args:
            profile_id: The Profile ID to update
            data: Dictionary containing fields to update
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The updated profile document

        Raises:
            HTTPForbidden: If caller is neither admin nor authorized for this profile
            HTTPNotFound: If profile does not exist
        """
        try:
            cls._check_permission(token, "update")

            mongo = MongoIO.get_instance()
            config = Config.get_instance()

            profile = mongo.get_document(config.PROFILE_COLLECTION_NAME, profile_id)
            if profile is None:
                raise HTTPNotFound(f"Profile {profile_id} not found")

            # Authorization check for non-admin callers
            if not is_admin(token):
                caller_profile_id = (
                    str(token.get("profile_id")) if token.get("profile_id") else None
                )
                caller_customer_id = (
                    str(token.get("customer_id")) if token.get("customer_id") else None
                )
                target_profile_id = str(profile.get("_id"))
                target_customer_id = (
                    str(profile.get("customer_id"))
                    if profile.get("customer_id")
                    else None
                )
                is_own_profile = (
                    caller_profile_id and caller_profile_id == target_profile_id
                )
                is_same_customer = (
                    caller_customer_id
                    and target_customer_id
                    and caller_customer_id == target_customer_id
                )

                if not (is_own_profile or is_same_customer):
                    raise HTTPForbidden(
                        f"Forbidden: insufficient permissions to update profile {profile_id}"
                    )

            # Strip system managed fields
            for field in SYSTEM_MANAGED_FIELDS:
                data.pop(field, None)

            # Stamp saved breadcrumb
            data["saved"] = breadcrumb

            encode_document(data, ID_PROPERTIES, DATE_PROPERTIES)

            updated = mongo.update_document(
                config.PROFILE_COLLECTION_NAME, profile_id, set_data=data
            )

            logger.info(f"Updated profile {profile_id} for user {token.get('user_id')}")
            return updated
        except (HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error updating profile {profile_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to update profile {profile_id}")
