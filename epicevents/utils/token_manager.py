import keyring
import json
import sentry_sdk
from cryptography.fernet import Fernet

SERVICE_NAME = "EpicEvents"


class TokenManager:
    """
    Manages the storage and retrieval of tokens for users.
    """

    @staticmethod
    def save_tokens(username: str, tokens: dict):
        """
        Saves the tokens and key to the keyring for the specified user.

        Args:
            username (str): The username of the user.
            tokens (dict): A dictionary containing the JWT and refresh tokens.
        """
        try:
            key = tokens['key']  # Use the provided key

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