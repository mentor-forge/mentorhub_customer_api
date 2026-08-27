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
from api_utils.services import ProfileService as SharedProfileService
from api_utils.services.profile_service import (
    ID_PROPERTIES,
    DATE_PROPERTIES,
    SYSTEM_MANAGED_FIELDS,
)
from api_utils.services.rbac import is_admin

logger = logging.getLogger(__name__)


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
                caller_user_id = token.get("user_id")

                target_profile_id = str(profile.get("_id"))
                target_customer_id = (
                    str(profile.get("customer_id"))
                    if profile.get("customer_id")
                    else None
                )
                target_name = profile.get("name")

                is_own_profile = (
                    caller_profile_id and caller_profile_id == target_profile_id
                ) or (caller_user_id and caller_user_id == target_name)
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

            mongo.update_document(config.PROFILE_COLLECTION_NAME, profile_id, data)

            updated = mongo.get_document(config.PROFILE_COLLECTION_NAME, profile_id)
            logger.info(f"Updated profile {profile_id} for user {token.get('user_id')}")
            return updated
        except (HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error updating profile {profile_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to update profile {profile_id}")
