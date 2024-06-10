from argon2 import PasswordHasher, exceptions
from sqlalchemy.orm import Session
from models.user import User
import sentry_sdk


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
            user = User(username=username, password=hashed_password, email=email, name=name, department_id=department_id)
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            sentry_sdk.capture_exception(e)
            session.rollback()
            raise

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
