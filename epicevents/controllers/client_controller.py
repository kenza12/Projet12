
from models.client import Client
from models.user import User
import sentry_sdk
from utils.token_manager import TokenManager
from utils.session_manager import get_session
from utils.data_validator import DataValidator
from utils.permissions import PermissionManager


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

    @staticmethod
    def create_client(token: str, full_name: str, email: str, phone: str, company_name: str, date_created: str, commercial_contact_id: int) -> bool:
        """
        Creates a new client if data is valid.
        """
        try:
            session = get_session()
            if not (DataValidator.validate_not_empty(full_name) and DataValidator.validate_email(email) and
                    DataValidator.validate_phone(phone)):
                raise ValueError("Invalid data provided for creating client.")

            client = Client(full_name=full_name, email=email, phone=phone, company_name=company_name, date_created=date_created, commercial_contact_id=commercial_contact_id)
            session.add(client)
            session.commit()
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

    @staticmethod
    def update_client(token: str, client_id: int, full_name: str = None, email: str = None, phone: str = None,
                      company_name: str = None, last_contact_date: str = None) -> bool:
        """
        Updates an existing client if data is valid.
        """
        try:
            session = get_session()
            client = session.query(Client).filter_by(id=client_id).first()
            if not client:
                raise ValueError("Client not found.")

            if full_name and DataValidator.validate_not_empty(full_name):
                client.full_name = full_name
            if email and DataValidator.validate_email(email):
                client.email = email
            if phone and DataValidator.validate_phone(phone):
                client.phone = phone
            if company_name:
                client.company_name = company_name
            if last_contact_date and DataValidator.validate_date(last_contact_date):
                client.last_contact_date = last_contact_date

            session.commit()
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False
        
    @staticmethod
    def get_client_id_by_name(client_name: str) -> int:
        """
        Retrieve the client ID based on the client name.
        Args:
            client_name (str): The name of the client.
        Returns:
            int: The ID of the client if found, otherwise None.
        """
        try:
            session = get_session()
            client = session.query(Client).filter_by(full_name=client_name).first()
            if client:
                return client.id
            return None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None