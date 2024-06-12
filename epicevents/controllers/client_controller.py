
from models.client import Client
import sentry_sdk
from utils.token_manager import TokenManager
from utils.session_manager import get_session


class ClientController:
    @staticmethod
    def get_all_clients(token: str) -> list:
        """
        Retrieves all clients if the user is authenticated and authorized.
        Args:
            token (str): JWT token of the authenticated user.
        Returns:
            list: List of Client objects.
        """
        try:
            key = TokenManager.load_key()
            payload = TokenManager.verify_token(token, key)
            if payload:
                session = get_session()
                clients = session.query(Client).all()
                return clients
            return []
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []
