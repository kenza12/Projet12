from sqlalchemy import inspect
from config import Config, SERVICE_NAME
from models.user import User
from models.department import Department
from utils.database_initializer import DatabaseInitializer
from controllers.user_controller import UserController
from utils.token_manager import TokenManager
import sentry_sdk
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import keyring
from controllers.client_controller import ClientController
from controllers.contract_controller import ContractController
from controllers.event_controller import EventController
from utils.session_manager import get_session_root, get_session
from datetime import datetime, date
from utils.permissions import PermissionManager

load_dotenv()


class MainController:
    """
    Manage database initialization, user authentication, token management, and CLI operations.
    """

    @staticmethod
    def set_use_test_database(use_test: bool):
        Config.set_use_test_database(use_test)

    @staticmethod
    def initialize_database() -> bool:
        """
        Initializes the database by performing all necessary steps.
        Returns True if initialization was successful, otherwise False.
        """
        try:
            initializer = DatabaseInitializer()
            initializer.initialize()
            print("Database initialized successfully.")
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error during database initialization: {e}")
            return False

    @staticmethod
    def is_database_initialized() -> bool:
        """
        Check if the database is initialized by inspecting if the User table exists.
        Returns True if the database is initialized, otherwise False.
        """
        try:
            session = get_session_root()
            inspector = inspect(session.bind)
            return 'User' in inspector.get_table_names()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

    @staticmethod
    def authenticate(username: str, password: str) -> dict:
        """
        Authenticates a user and returns JWT and refresh tokens if successful.
        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        Returns:
            dict: JWT and refresh tokens if authentication is successful, otherwise None.
        """
        try:
            session = get_session_root()
            if UserController.authenticate_user(session, username, password):
                user = session.query(User).filter_by(username=username).first()
                key = Fernet.generate_key().decode()
                token = TokenManager.generate_token(user, key)
                refresh_token = TokenManager.generate_refresh_token(user, key)
                tokens = {"token": token, "refresh_token": refresh_token, "key": key}
                TokenManager.save_tokens(username, tokens)
                return tokens
            return None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @staticmethod
    def create_users() -> bool:
        """
        Create initial users with their respective departments from environment variables.
        Returns True if user creation was successful, otherwise False.
        """
        try:
            session = get_session_root()

            departments = {
                "Commercial": session.query(Department).filter_by(name="Commercial").first().id,
                "Support": session.query(Department).filter_by(name="Support").first().id,
                "Gestion": session.query(Department).filter_by(name="Gestion").first().id
            }

            users = [
                {
                    "username": os.getenv("USER1_USERNAME"),
                    "password": os.getenv("USER1_PASSWORD"),
                    "email": os.getenv("USER1_EMAIL"),
                    "name": os.getenv("USER1_NAME"),
                    "department_id": departments[os.getenv("USER1_DEPARTMENT")]
                },
                {
                    "username": os.getenv("USER2_USERNAME"),
                    "password": os.getenv("USER2_PASSWORD"),
                    "email": os.getenv("USER2_EMAIL"),
                    "name": os.getenv("USER2_NAME"),
                    "department_id": departments[os.getenv("USER2_DEPARTMENT")]
                },
                {
                    "username": os.getenv("USER3_USERNAME"),
                    "password": os.getenv("USER3_PASSWORD"),
                    "email": os.getenv("USER3_EMAIL"),
                    "name": os.getenv("USER3_NAME"),
                    "department_id": departments[os.getenv("USER3_DEPARTMENT")]
                }
            ]

            for user_data in users:
                existing_user = session.query(User).filter_by(username=user_data['username']).first()
                if existing_user:
                    print(f"User {user_data['username']} already exists. Skipping creation.")
                else:
                    UserController.create_user(session, **user_data)
            
            print("Users creation process completed.")
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating users: {e}")
            return False

    @staticmethod
    def refresh_token(username: str) -> str:
        """
        Refreshes the JWT token using the refresh token.
        
        Args:
            username (str): The username of the user.
        
        Returns:
            str: The newly generated JWT token if refresh is successful, otherwise None.
        """
        try:
            tokens = TokenManager.load_tokens(username)
            if tokens and 'refresh_token' in tokens and 'key' in tokens:
                refresh_token = tokens['refresh_token']
                key = tokens['key']
                new_token = TokenManager.refresh_token(refresh_token, key)
                if new_token:
                    tokens['token'] = new_token
                    TokenManager.save_tokens(username, tokens)
                    return new_token
            return None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Failed to refresh token for {username}")
            return None

    @staticmethod
    def check_token_status(username: str) -> str:
        """
        Checks the token status and informs the user if it needs to be refreshed.
        Args:
            username (str): The username of the user.
        Returns:
            str: The status of the token ("expired", "active", or "no_token").
        """
        tokens = TokenManager.load_tokens(username)
        if tokens and 'token' in tokens and 'key' in tokens:
            if TokenManager.is_token_expired(tokens['token'], tokens['key']):
                return "expired"
            else:
                return "active"
        else:
            return "no_token"

    @staticmethod
    def logout() -> str:
        """
        Logs out the current user by deleting the stored tokens.
        
        Returns:
            str: The status of the logout operation ("logged_out", "no_session", or error message).
        """
        try:
            # Retrieve the current username from keyring
            username = keyring.get_password(SERVICE_NAME, "current_user")
            if username:
                tokens = TokenManager.load_tokens(username)
                if tokens:
                    TokenManager.delete_tokens(username)
                    return "logged_out"
                else:
                    return "no_session"
            else:
                return "no_session"
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return str(e)

    @staticmethod
    def get_clients() -> list:
        """
        Retrieves all clients if the user is authenticated and authorized.
        Returns:
            list: List of Client objects or an empty list if not authorized.
        """
        username = keyring.get_password(SERVICE_NAME, "current_user")
        if not username:
            return []
        tokens = TokenManager.load_tokens(username)
        if tokens and 'token' in tokens and 'key' in tokens:
            return ClientController.get_all_clients(tokens['token'])
        return []

    @staticmethod
    def get_contracts() -> list:
        """
        Retrieves all contracts if the user is authenticated and authorized.
        Returns:
            list: List of Contract objects or an empty list if not authorized.
        """
        username = keyring.get_password(SERVICE_NAME, "current_user")
        if not username:
            return []
        tokens = TokenManager.load_tokens(username)
        if tokens and 'token' in tokens and 'key' in tokens:
            return ContractController.get_all_contracts(tokens['token'])
        return []

    @staticmethod
    def get_events() -> list:
        """
        Retrieves all events if the user is authenticated and authorized.
        Returns:
            list: List of Event objects or an empty list if not authorized.
        """
        username = keyring.get_password(SERVICE_NAME, "current_user")
        if not username:
            return []
        tokens = TokenManager.load_tokens(username)
        if tokens and 'token' in tokens and 'key' in tokens:
            return EventController.get_all_events(tokens['token'])
        return []

    @staticmethod
    def verify_authentication_and_authorization(action: str) -> tuple:
        """
        Verify the user's authentication and authorization for a specific action.
        
        Args:
            action (str): The action to be authorized (e.g., 'create_client', 'update_contract').

        Returns:
            tuple: (token, user, True) if authorized, otherwise (None, None, False).
        """
        try:
            username = keyring.get_password(SERVICE_NAME, "current_user")
            tokens = TokenManager.load_tokens(username)
            if tokens:
                token = tokens['token']
                key = tokens['key']
                payload = TokenManager.verify_token(token, key)
                if payload:
                    session = get_session()
                    user = session.query(User).filter_by(id=payload['user_id']).first()
                    permission_check_method = getattr(PermissionManager, f"can_{action}", None)
                    if permission_check_method and permission_check_method(user):
                        return token, user, True
        except Exception as e:
            sentry_sdk.capture_exception(e)
        return None, None, False

    @staticmethod
    def update_client(client_id: int, full_name: str = None, email: str = None, phone: str = None,
                      company_name: str = None, last_contact_date: str = None) -> bool:
        """
        Update an existing client if the user is authorized.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('update_client')
        if authorized:
            try:
                return ClientController.update_client(token, client_id, full_name, email, phone, company_name, last_contact_date)
            except Exception as e:
                sentry_sdk.capture_exception(e)
        return False

    @staticmethod
    def create_contract(client_id: int, total_amount: float, amount_due: float, signed: bool) -> str:
        """
        Create a new contract if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('create_contract')
        if authorized:
            try:
                date_created = datetime.now().date()
                # Fetch the commercial_contact_id from the client
                commercial_contact_id = ClientController.get_commercial_contact_id(client_id)
                if ContractController.create_contract(client_id, commercial_contact_id, total_amount, amount_due, date_created, signed):
                    return "Contract created successfully."
                else:
                    return "Failed to create contract. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error creating contract: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def update_contract(contract_id: int, client_id: int = None, total_amount: float = None, amount_due: float = None, signed: bool = None) -> str:
        """
        Update an existing contract if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('update_contract')
        if authorized:
            try:
                if user.department.name == "Commercial":
                    contract = ContractController.get_contract_by_id(contract_id)
                    if contract.commercial_contact_id != user.id:
                        return "You are not authorized to update this contract."

                success = ContractController.update_contract(contract_id, client_id, total_amount, amount_due, signed)
                if success:
                    return "Contract updated successfully."
                else:
                    return "Failed to update contract. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error updating contract: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def update_collaborator(user_id: int, username: str = None, password: str = None, email: str = None, name: str = None, department_id: int = None) -> str:
        """
        Update an existing collaborator if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('update_user')
        if authorized:
            try:
                session = get_session_root()
                if UserController.update_user(session, user_id, username, password, email, name, department_id):
                    return "Collaborator updated successfully."
                else:
                    return "Failed to update collaborator. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error updating collaborator: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def create_event(contract_id: int, event_name: str, event_date_start: str,
                    event_date_end: str, location: str, attendees: int, notes: str) -> str:
        """
        Create a new event if the user is authorized and the contract is signed.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('create_event')
        if authorized:
            try:
                client_id = ContractController.get_client_id_by_contract_id(contract_id)
                support_contact_id = None  # Initially set to None until a support contact is assigned
                success = EventController.create_event(contract_id, client_id, event_name, event_date_start, event_date_end, support_contact_id, location, attendees, notes)
                if success:
                    return "Event created successfully."
                else:
                    return "Failed to create event. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error creating event: {e}"
        else:
            return "You are not authorized to perform this action."


    @staticmethod
    def update_event(event_id: int, contract_id: int = None, client_id: int = None, event_name: str = None,
                     event_date_start: str = None, event_date_end: str = None, support_contact_id: int = None,
                     location: str = None, attendees: int = None, notes: str = None) -> str:
        """
        Update an existing event if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized_support = MainController.verify_authentication_and_authorization('update_event')
        token_gestion, user_gestion, authorized_gestion = MainController.verify_authentication_and_authorization('update_event_support_contact')

        if authorized_support or authorized_gestion:
            try:
                if authorized_gestion and support_contact_id is not None:
                    # If Gestion department, only update support_contact_id
                    success = EventController.update_event(token_gestion, user_gestion, event_id, support_contact_id=support_contact_id)
                elif authorized_support:
                    # If Support department, update all fields
                    event = EventController.get_event_by_id(event_id)
                    if event.support_contact_id != user.id:
                        return "You are not authorized to update this event."
                    success = EventController.update_event(token, user, event_id, contract_id, client_id, event_name, event_date_start, event_date_end, support_contact_id, location, attendees, notes)
                else:
                    return "You are not authorized to update events."

                if success:
                    return "Event updated successfully."
                else:
                    return "Failed to update event. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error updating event: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def create_collaborator(username: str, password: str, email: str, name: str, department_id: int) -> str:
        """
        Create a new collaborator if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('manage_users')
        if authorized:
            try:
                session = get_session_root()
                UserController.create_user(session, username, password, email, name, department_id)
                return "Collaborator created successfully."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error creating collaborator: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def update_collaborator(user_id: int, username: str = None, password: str = None, email: str = None, name: str = None, department_id: int = None) -> str:
        """
        Update an existing collaborator if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('manage_users')
        if authorized:
            try:
                session = get_session_root()
                if UserController.update_user(session, user_id, username, password, email, name, department_id):
                    return "Collaborator updated successfully."
                else:
                    return "Failed to update collaborator. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error updating collaborator: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def delete_collaborator(user_id: int) -> str:
        """
        Delete an existing collaborator if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('manage_users')
        if authorized:
            try:
                session = get_session_root()
                if UserController.delete_user(session, user_id):
                    return "Collaborator deleted successfully."
                else:
                    return "Failed to delete collaborator. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error deleting collaborator: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def get_current_user():
        """
        Retrieve the current authenticated user.
        """
        try:
            username = keyring.get_password(SERVICE_NAME, "current_user")
            return username
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @staticmethod
    def get_user_role(username):
        """
        Retrieve the role of the given user.
        """
        try:
            session = get_session()
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user.department.name
            return None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @staticmethod
    def filter_events(filters: dict) -> list:
        """
        Filter events based on specified criteria.
        Args:
            filters (dict): Dictionary of filters.
        Returns:
            list: List of filtered Event objects.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('filter_events')
        if authorized:
            try:
                if user.department.name == "Support":
                    filters['support_contact_id'] = user.id
                return EventController.get_filtered_events(filters)
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return []
        else:
            return []

    @staticmethod
    def create_client(full_name: str, email: str, phone: str, company_name: str) -> str:
        """
        Create a new client if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('create_client')
        if authorized:
            try:
                commercial_contact_id = user.id
                date_created = date.today()
                success = ClientController.create_client(full_name, email, phone, company_name, date_created, commercial_contact_id)
                if success:
                    return "Client created successfully."
                else:
                    return "Failed to create client. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error creating client: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def update_client(client_id: int, full_name: str = None, email: str = None, phone: str = None, company_name: str = None) -> str:
        """
        Update an existing client if the user is authorized.
        Returns:
            str: Message indicating the result of the operation.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('update_client')
        if authorized:
            try:
                success = ClientController.update_client(client_id, full_name, email, phone, company_name)
                if success:
                    return "Client updated successfully."
                else:
                    return "Failed to update client. Please check the input data."
            except ValueError as ve:
                return f"Validation Error: {ve}"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return f"Error updating client: {e}"
        else:
            return "You are not authorized to perform this action."

    @staticmethod
    def filter_contracts(filters: dict):
        """
        Filter contracts based on specified criteria.
        Args:
            filters (dict): Dictionary of filters.
        Returns:
            list: List of filtered Contract objects.
        """
        token, user, authorized = MainController.verify_authentication_and_authorization('filter_contracts')
        if authorized:
            try:
                return ContractController.get_filtered_contracts(filters)
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return []
        else:
            raise PermissionError("You are not authorized to perform this action.")

    @staticmethod
    def start_cli():
        """
        Starts the CLI.
        """
        from views.main_views import start_cli
        start_cli()
