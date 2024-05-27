from sqlalchemy import create_engine, text
from config import Config
import sentry_sdk
import os


class DatabaseInitializer:
    """Creating the database, importing the schema, and setting up the non-privileged user."""
    
    def __init__(self):
        """
        Sets up the connection to the MySQL server using the administrator's credentials.
        It constructs the database URI without specifying a database name and creates an SQLAlchemy
        engine for managing the connection.
        """
        try:
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
            with self.engine.connect() as connection:
                print("Creating database...")
                connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET UTF8"))
                print("Database created successfully.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating database: {e}")

    def import_schema(self):
        """
        Imports the SQL schema from a file if it exists.
        """
        try:
            db_uri_with_name = Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD)
            schema_engine = create_engine(db_uri_with_name)
            if os.path.exists("schema.sql"):
                with schema_engine.connect() as connection:
                    print(f"Importing schema from schema.sql to {Config.DB_NAME}...")
                    with open("schema.sql", "r") as file:
                        schema_sql = file.read()
                        for statement in schema_sql.split(';'):
                            if statement.strip():
                                connection.execute(text(statement))
                    print("Schema imported successfully.")
            else:
                print("schema.sql file not found. Please ensure the file exists in the current directory.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error importing schema: {e}")

    def create_user(self):
        """
        Creates a non-privileged user and grants necessary privileges.
        """
        try:
            db_uri_with_name = Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD)
            user_engine = create_engine(db_uri_with_name)
            with user_engine.connect() as connection:
                print("Creating user...")
                create_user_sql = text(f"CREATE USER IF NOT EXISTS '{Config.DB_USER}'@'localhost' IDENTIFIED BY '{Config.DB_PASSWORD}'")
                connection.execute(create_user_sql)
                connection.execute(text(f"GRANT SELECT, INSERT, UPDATE ON {Config.DB_NAME}.* TO '{Config.DB_USER}'@'localhost'"))
                connection.execute(text("FLUSH PRIVILEGES"))
                print("User created successfully.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating user: {e}")

    def initialize(self):
        """
        Initialize the database by performing all necessary steps.
        """
        try:
            self.create_database()
            # Reinitialize the engine with the new database URI including the database name
            self.engine = create_engine(Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD))
            self.import_schema()
            self.create_user()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Failed to initialize the database: {e}")