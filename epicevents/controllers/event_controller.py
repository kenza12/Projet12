from models.event import Event
import sentry_sdk
from utils.token_manager import TokenManager
from utils.session_manager import get_session


class EventController:
    @staticmethod
    def get_all_events(token: str) -> list:
        """
        Retrieves all events if the user is authenticated and authorized.
        Args:
            token (str): JWT token of the authenticated user.
        Returns:
            list: List of Event objects.
        """
        try:
            key = TokenManager.load_key()
            payload = TokenManager.verify_token(token, key)
            if payload:
                session = get_session()
                events = session.query(Event).all()
                return events
            return []
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []
