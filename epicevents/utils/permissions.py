
from models.user import User
import sentry_sdk


class PermissionManager:
    """
    Manages user permissions based on their roles.
    """

    @staticmethod
    def can_create_client(user: User) -> bool:
        return user.department.name == "Commercial"

    @staticmethod
    def can_update_client(user: User) -> bool:
        return user.department.name == "Commercial"

    @staticmethod
    def can_create_contract(user: User) -> bool:
        return user.department.name == "Gestion"

    @staticmethod
    def can_update_contract(user: User) -> bool:
        return user.department.name in ["Gestion", "Commercial"]

    @staticmethod
    def can_create_event(user: User) -> bool:
        return user.department.name == "Commercial"

    @staticmethod
    def can_update_event(user: User) -> bool:
        return user.department.name in ["Support"]

    @staticmethod
    def can_update_event_support_contact(user: User) -> bool:
        return user.department.name == "Gestion"

    @staticmethod
    def can_manage_users(user: User) -> bool:
        return user.department.name == "Gestion"

    @staticmethod
    def get_user_role(user: User) -> str:
        """
        Returns the role/department of the user.
        """
        try:
            return user.department.name
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @staticmethod
    def can_filter_events(user: User) -> bool:
        return user.department.name in ["Gestion", "Support"]

    @staticmethod
    def can_filter_contracts(user: User) -> bool:
        return user.department.name == "Commercial"

    @staticmethod
    def can_manage_events_support(user: User) -> bool:
        return user.department.name == "Support"

    @staticmethod
    def can_manage_events_gestion(user: User) -> bool:
        return user.department.name == "Gestion"