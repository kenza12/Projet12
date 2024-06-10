import jwt
import datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError
from models.user import User
import sentry_sdk
from config import Config
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class PermissionManager:
    """
    Manages JWT creation and verification for user authentication and authorization.
    """

    @staticmethod
    def generate_token(user: User, key: str) -> str:
        """
        Generates a JWT token for the given user.

        Args:
            user (User): The user object containing user details.
            key (str): The secret key used to sign the token.

        Returns:
            str: The generated JWT token.
        """
        try:
            secret_key = key.encode()
            payload = {
                'user_id': user.id,
                'username': user.username,
                'department': user.department.name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Extend expiration for better testing
            }
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            return token
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @staticmethod
    def generate_refresh_token(user: User, key: str) -> str:
        """
        Generates a refresh token for the given user.

        Args:
            user (User): The user object containing user details.
            key (str): The secret key used to sign the token.

        Returns:
            str: The generated refresh token.
        """
        try:
            secret_key = key.encode()
            payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # Extend expiration for refresh token
            }
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            return token
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @staticmethod
    def verify_token(token: str, key: str) -> dict:
        """
        Verifies the given JWT token.

        Args:
            token (str): The JWT token to verify.
            key (str): The secret key used to decode the token.

        Returns:
            dict: The decoded token payload.
        """
        try:
            secret_key = key.encode()
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except ExpiredSignatureError as e:
            sentry_sdk.capture_exception(e)
            print("Token has expired")
            raise
        except InvalidTokenError as e:
            sentry_sdk.capture_exception(e)
            print("Token is invalid")
            raise
        except InvalidSignatureError as e:
            sentry_sdk.capture_exception(e)
            print("Token signature is invalid")
            raise

    @staticmethod
    def is_token_expired(token: str, key: str) -> bool:
        """
        Checks if the given JWT token has expired.

        Args:
            token (str): The JWT token to check.
            key (str): The secret key used to decode the token.

        Returns:
            bool: True if the token has expired, False otherwise.
        """
        try:
            secret_key = key.encode()
            jwt.decode(token, secret_key, algorithms=['HS256'])
            return False
        except ExpiredSignatureError:
            return True
        except InvalidTokenError as e:
            sentry_sdk.capture_exception(e)
            return True

    @staticmethod
    def refresh_token(refresh_token: str, key: str) -> str:
        """
        Refreshes the JWT token using the given refresh token.

        Args:
            refresh_token (str): The refresh token to use for generating a new JWT token.
            key (str): The secret key used to decode the token.

        Returns:
            str: The newly generated JWT token.
        """
        try:
            payload = PermissionManager.verify_token(refresh_token, key)
            user_id = payload['user_id']
            
            engine = create_engine(Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD))
            Session = sessionmaker(bind=engine)
            session = Session()
            user = session.query(User).filter_by(id=user_id).first()
            
            if user:
                new_token = PermissionManager.generate_token(user, key)
                return new_token
            else:
                raise InvalidTokenError("User not found.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise
