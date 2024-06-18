from models.contract import Contract
from models.user import User
import sentry_sdk
from utils.token_manager import TokenManager
from utils.session_manager import get_session
from utils.data_validator import DataValidator
from utils.permissions import PermissionManager


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
    
    @staticmethod
    def create_contract(token: str, client_id: int, commercial_contact_id: int, total_amount: float, amount_due: float,
                        date_created: str, signed: bool) -> bool:
        """
        Creates a new contract if data is valid.
        """
        try:
            session = get_session()
            contract = Contract(client_id=client_id, commercial_contact_id=commercial_contact_id, total_amount=total_amount,
                                amount_due=amount_due, date_created=date_created, signed=signed)
            session.add(contract)
            session.commit()
            return True
        except ValueError as ve:
            sentry_sdk.capture_exception(ve)
            print(f"Validation Error: {ve}")
            return False
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating contract: {e}")
            return False

    @staticmethod
    def update_contract(token: str, contract_id: int, client_id: int = None, commercial_contact_id: int = None,
                        total_amount: float = None, amount_due: float = None, date_created: str = None, signed: bool = None) -> bool:
        """
        Updates an existing contract if data is valid.
        """
        try:
            session = get_session()
            contract = session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                raise ValueError("Contract not found.")

            if client_id:
                contract.client_id = client_id
            if commercial_contact_id:
                contract.commercial_contact_id = commercial_contact_id
            if total_amount:
                contract.total_amount = total_amount
            if amount_due:
                contract.amount_due = amount_due
            if date_created and DataValidator.validate_date(date_created):
                contract.date_created = date_created
            if signed is not None:
                contract.signed = signed

            session.commit()
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False