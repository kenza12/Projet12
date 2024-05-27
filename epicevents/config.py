from dotenv import load_dotenv, find_dotenv
import os
import sentry_sdk

# Load environment variables from the .env file
load_dotenv(find_dotenv())

class Config:
    """
    Configuration class to load and provide access to database configuration variables.

    Attributes are loaded from environment variables.
    """
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')

    ADMIN_DB_USER = os.getenv('ADMIN_DB_USER')
    ADMIN_DB_PASSWORD = os.getenv('ADMIN_DB_PASSWORD')
    SENTRY_DSN = os.getenv('SENTRY_DSN')

    @staticmethod
    def get_db_uri(user=None, password=None):
        """
        Constructs a database URI for the given user and password.
        
        If no user or password is provided, the default database user and password are used.

        Args:
            user (str): The database user.
            password (str): The database user's password.

        Returns:
            str: The constructed database URI.
        """
        user = user or Config.DB_USER
        password = password or Config.DB_PASSWORD
        return f"mysql+mysqlconnector://{user}:{password}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"

    @staticmethod
    def validate():
        """
        Validates that all required environment variables are set.
        """
        required_vars = [
            'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
            'DB_HOST', 'DB_PORT', 'ADMIN_DB_USER', 'ADMIN_DB_PASSWORD', 'SENTRY_DSN'
        ]
        for var in required_vars:
            if not getattr(Config, var):
                raise ValueError(f"The environment variable {var} is not set.")

# Initialize Sentry
sentry_sdk.init(dsn=Config.SENTRY_DSN, traces_sample_rate=1.0)