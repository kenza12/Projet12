from dotenv import load_dotenv, find_dotenv
import os
import sentry_sdk
from sqlalchemy.ext.declarative import declarative_base


def reload_environment():
    """
    Load environment variables
    """
    # Clear any existing environment variables
    for key in list(os.environ.keys()):
        if key in os.environ:
            del os.environ[key]
    
    # Load environment variables from the .env file
    load_dotenv(find_dotenv())

# Load environment variables
reload_environment()

# Service name for keyring
SERVICE_NAME = "EpicEvents"

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

    TEST_DB_NAME = os.getenv('TEST_DB_NAME')
    ADMIN_DB_USER = os.getenv('ADMIN_DB_USER')
    ADMIN_DB_PASSWORD = os.getenv('ADMIN_DB_PASSWORD')
    SENTRY_DSN = os.getenv('SENTRY_DSN')

    @staticmethod
    def get_db_uri(user=None, password=None, test=False):
        """
        Constructs a database URI for the given user and password.
        If no user or password is provided, the default database user and password are used.

        Args:
            user (str): The database user.
            password (str): The database user's password.
            test (bool): Use test database if True.

        Returns:
            str: The constructed database URI.
        """
        user = user or Config.DB_USER
        password = password or Config.DB_PASSWORD
        db_name = Config.TEST_DB_NAME if test else Config.DB_NAME
        return f"mysql+mysqlconnector://{user}:{password}@{Config.DB_HOST}:{Config.DB_PORT}/{db_name}"

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

# Define the Base class for SQLAlchemy models
Base = declarative_base()
