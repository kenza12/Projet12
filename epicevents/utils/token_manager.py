import jwt
import datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError
from models.user import User
import sentry_sdk
from config import Config
from utils.session_manager import get_session_root
import keyring
import json
from cryptography.fernet import Fernet

SERVICE_NAME = "EpicEvents"

class TokenManager:
    """
    Manages JWT creation, verification, and storage/retrieval of tokens for users.
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
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
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
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
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
    def refresh_token(refresh_token: str, key: str, test=False) -> str:
        """
        Refreshes the JWT token using the given refresh token.

        Args:
            refresh_token (str): The refresh token to use for generating a new JWT token.
            key (str): The secret key used to decode the token.

        Returns:
            str: The newly generated JWT token.
        """
        try:
            payload = TokenManager.verify_token(refresh_token, key)
            user_id = payload['user_id']
            
            session = get_session_root(test=test)
            user = session.query(User).filter_by(id=user_id).first()
            
            if user:
                new_token = TokenManager.generate_token(user, key)
                return new_token
            else:
                raise InvalidTokenError("User not found.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @staticmethod
    def save_tokens(username: str, tokens: dict):
        """
        Saves the tokens and key to the keyring for the specified user.

        Args:
            username (str): The username of the user.
            tokens (dict): A dictionary containing the JWT and refresh tokens.
        """
        try:
            key = tokens['key']

            # Encrypt the tokens with the key
            fernet = Fernet(key.encode())
            encrypted_tokens = fernet.encrypt(json.dumps(tokens).encode()).decode()

            # Save the encrypted tokens and the key to keyring
            keyring.set_password(SERVICE_NAME, f"{username}_tokens", encrypted_tokens)
            keyring.set_password(SERVICE_NAME, f"{username}_key", key)

            # Store the current username
            keyring.set_password(SERVICE_NAME, "current_user", username)

            print(f"Saved tokens for {username}")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @staticmethod
    def load_tokens(username: str) -> dict:
        """
        Loads the tokens and key from the keyring for the specified user.

        Args:
            username (str): The username of the user.

        Returns:
            dict: A dictionary containing the JWT and refresh tokens if available, otherwise None.
        """
        try:
            # Load the encrypted tokens and the key from keyring
            encrypted_tokens = keyring.get_password(SERVICE_NAME, f"{username}_tokens")
            key = keyring.get_password(SERVICE_NAME, f"{username}_key")

            if encrypted_tokens and key:
                # Decrypt the tokens with the key
                fernet = Fernet(key.encode())
                decrypted_tokens = fernet.decrypt(encrypted_tokens.encode()).decode()
                tokens = json.loads(decrypted_tokens)
                tokens['key'] = key

                print(f"Loaded tokens for {username}")
                return tokens

            return None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @staticmethod
    def delete_tokens(username: str):
        """
        Deletes the tokens and key from the keyring for the specified user.

        Args:
            username (str): The username of the user.
        """
        try:
            keyring.delete_password(SERVICE_NAME, f"{username}_tokens")
            keyring.delete_password(SERVICE_NAME, f"{username}_key")
            keyring.delete_password(SERVICE_NAME, "current_user")
            print(f"Deleted tokens for {username}")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @staticmethod
    def load_key() -> str:
        """
        Loads the key from keyring for the current user.

        Returns:
            str: The key if available, otherwise None.
        """
        username = keyring.get_password(SERVICE_NAME, "current_user")
        if username:
            key = keyring.get_password(SERVICE_NAME, f"{username}_key")
            return key
        return None
