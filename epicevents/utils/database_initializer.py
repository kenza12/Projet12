from sqlalchemy import create_engine, text
from config import Config, Base
import sentry_sdk
from models.user import User
from models.department import Department
from models.client import Client
from models.contract import Contract
from models.event import Event


class DatabaseInitializer:
    """Creating the database and setting up the non-privileged user."""

    def __init__(self, test=False):
        """
        Initializes the DatabaseInitializer with the admin database URI without specifying the database name.
        It also creates an SQLAlchemy engine for connecting to the MySQL server using the constructed URI.
        """
        try:
            self.test = test
            self.admin_db_uri = f"mysql+mysqlconnector://{Config.ADMIN_DB_USER}:{Config.ADMIN_DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/"
            self.engine = create_engine(self.admin_db_uri)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Failed to initialize DatabaseInitializer: {e}")

    def create_database(self):
        """
        Creates the database if it does not already exist.
        """
        try:
            db_name = Config.TEST_DB_NAME if self.test else Config.DB_NAME
            with self.engine.connect() as connection:
                print(f"Creating database {db_name}...")
                connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET UTF8"))
                print(f"Database {db_name} created successfully.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating database: {e}")

    def create_user(self):
        """
        Creates a non-privileged user and grants necessary privileges.
        """
        try:
            db_name = Config.TEST_DB_NAME if self.test else Config.DB_NAME
            db_uri_with_name = Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD, self.test)
            user_engine = create_engine(db_uri_with_name)
            with user_engine.connect() as connection:
                print("Creating user...")
                create_user_sql = text(f"CREATE USER IF NOT EXISTS '{Config.DB_USER}'@'localhost' IDENTIFIED BY '{Config.DB_PASSWORD}'")
                connection.execute(create_user_sql)
                connection.execute(text(f"GRANT SELECT, INSERT, UPDATE ON {db_name}.* TO '{Config.DB_USER}'@'localhost'"))
                connection.execute(text("FLUSH PRIVILEGES"))
                print("User created successfully.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating user: {e}")

    def create_tables(self):
        """
        Creates tables for the defined models.
        """
        try:
            db_uri_with_admin = Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD, self.test)
            engine_with_db = create_engine(db_uri_with_admin)
            print("Engine created with admin credentials:", engine_with_db)
            print("Creating tables...")
            Base.metadata.create_all(engine_with_db)
            # print("Metadata tables:", Base.metadata.tables)
            print("Tables created successfully.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating tables: {e}")

    def initialize(self):
        """
        Initialize the database by performing all necessary steps.
        """
        try:
            self.create_database()
            self.create_user()
            self.create_tables()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Failed to initialize the database: {e}")
