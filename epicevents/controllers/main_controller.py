from sqlalchemy import create_engine, inspect
from config import Config, SERVICE_NAME
from models.user import User
from models.department import Department
from utils.permissions import PermissionManager
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
from utils.session_manager import get_session_root

load_dotenv()


class MainController:
    """
    Manage database initialization, user authentication, token management, and CLI operations.
    """

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
                token = PermissionManager.generate_token(user, key)
                refresh_token = PermissionManager.generate_refresh_token(user, key)
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
    def refresh_token(username: str, password: str) -> str:
        """
        Refreshes the JWT token using the refresh token.
        
        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        
        Returns:
            str: The newly generated JWT token if refresh is successful, otherwise None.
        """
        try:
            tokens = TokenManager.load_tokens(username)
            if tokens and 'refresh_token' in tokens and 'key' in tokens:
                refresh_token = tokens['refresh_token']
                key = tokens['key']
                new_token = PermissionManager.refresh_token(refresh_token, key)
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
            if PermissionManager.is_token_expired(tokens['token'], tokens['key']):
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
    def start_cli():
        """
        Starts the CLI.
        """
        from views.cli_views import start_cli
        start_cli()
