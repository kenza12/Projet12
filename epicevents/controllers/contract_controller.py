from models.contract import Contract
import sentry_sdk
from utils.token_manager import TokenManager
from utils.session_manager import get_session


class ContractController:
    @staticmethod
    def get_all_contracts(token: str) -> list:
        """
        Retrieves all contracts if the user is authenticated and authorized.
        Args:
            token (str): JWT token of the authenticated user.
        Returns:
            list: List of Contract objects.
        """
        try:
            key = TokenManager.load_key()
            payload = TokenManager.verify_token(token, key)
            if payload:
                session = get_session()
                contracts = session.query(Contract).all()
                return contracts
            return []
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []
