from argon2 import PasswordHasher, exceptions
from sqlalchemy.orm import Session
from models.user import User
import sentry_sdk
from utils.session_manager import get_session


class UserController:
    """
    Managing user-related operations, including password hashing, user creation, and user authentication.
    """

    ph = PasswordHasher()

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes the provided password using Argon2.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password.
        """
        return UserController.ph.hash(password)

    @staticmethod
    def create_user(session: Session, username: str, password: str, email: str, name: str, department_id: int):
        """
        Creates a new user in the database with the provided details.

        Args:
            session (Session): The SQLAlchemy session.
            username (str): The username of the new user.
            password (str): The plain text password of the new user.
            email (str): The email address of the new user.
            name (str): The full name of the new user.
            department_id (int): The ID of the department the user belongs to.

        Returns:
            User: The created User object.
        """
        try:
            hashed_password = UserController.hash_password(password)
            user = User(
                username=username, password=hashed_password, email=email, name=name, department_id=department_id
            )
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            sentry_sdk.capture_exception(e)
            session.rollback()
            raise

    @staticmethod
    def update_user(
        session: Session,
        user_id: int,
        username: str = None,
        password: str = None,
        email: str = None,
        name: str = None,
        department_id: int = None,
    ) -> bool:
        """
        Updates an existing user in the database with the provided details.

        Args:
            session (Session): The SQLAlchemy session.
            user_id (int): The ID of the user to update.
            username (str, optional): The new username for the user.
            password (str, optional): The new password for the user.
            email (str, optional): The new email for the user.
            name (str, optional): The new full name for the user.
            department_id (int, optional): The new department ID for the user.

        Returns:
            bool: True if the update is successful, False otherwise.
        """
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False

            if username:
                user.username = username
            if password:
                user.password = UserController.hash_password(password)
            if email:
                user.email = email
            if name:
                user.name = name
            if department_id:
                user.department_id = department_id

            session.commit()
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            session.rollback()
            return False

    @staticmethod
    def delete_user(session: Session, user_id: int) -> bool:
        """
        Deletes an existing user from the database.

        Args:
            session (Session): The SQLAlchemy session.
            user_id (int): The ID of the user to delete.

        Returns:
            bool: True if the deletion is successful, False otherwise.
        """
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False

            session.delete(user)
            session.commit()
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            session.rollback()
            return False

    @staticmethod
    def authenticate_user(session: Session, username: str, password: str) -> bool:
        """
        Authenticates a user by verifying the provided password.

        Args:
            session (Session): The SQLAlchemy session.
            username (str): The username of the user attempting to authenticate.
            password (str): The plain text password provided by the user.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                try:
                    UserController.ph.verify(user.password, password)
                    return True
                except exceptions.VerifyMismatchError:
                    return False
            return False
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @staticmethod
    def get_user_id_by_username(username: str) -> int:
        """
        Retrieve the user ID based on the user's username.
        Args:
            username (str): The username of the user.
        Returns:
            int: The ID of the user if found, otherwise None.
        """
        try:
            session = get_session()
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user.id
            return None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @staticmethod
    def get_user_id_by_name(name: str) -> int:
        """
        Retrieve the user ID based on the user's name.
        Args:
            name (str): The name of the user.
        Returns:
            int: The ID of the user if found, otherwise None.
        """
        try:
            session = get_session()
            user = session.query(User).filter_by(name=name).first()
            if user:
                print(f"User ID for {name}: {user.id}")
                return user.id
            return None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @staticmethod
    def user_exists(user_id: int) -> bool:
        """
        Check if a user with the given ID exists in the database.
        Args:
            user_id (int): The ID of the user.
        Returns:
            bool: True if the user exists, otherwise False.
        """
        try:
            session = get_session()
            user = session.query(User).filter_by(id=user_id).first()
            return user is not None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """
        Retrieve the user based on the user's ID.
        Args:
            user_id (int): The ID of the user.
        Returns:
            User: The User object if found, otherwise None.
        """
        try:
            session = get_session()
            user = session.query(User).filter_by(id=user_id).first()
            return user
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None
