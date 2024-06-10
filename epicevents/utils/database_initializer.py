from config import Config, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
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
            self.user_db_uri = Config.get_db_uri(Config.DB_USER, Config.DB_PASSWORD, test)
            self.engine = create_engine(self.admin_db_uri)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Failed to initialize DatabaseInitializer: {e}")

    def create_database(self):
        """
        Creates the database if it does not already exist using the admin user.
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
            with self.engine.connect() as connection:
                print("Creating user...")
                create_user_sql = text(f"CREATE USER IF NOT EXISTS '{Config.DB_USER}'@'localhost' IDENTIFIED BY '{Config.DB_PASSWORD}'")
                connection.execute(create_user_sql)
                connection.execute(text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {db_name}.* TO '{Config.DB_USER}'@'localhost'"))
                connection.execute(text("FLUSH PRIVILEGES"))
                print("User created successfully.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating user: {e}")

    def create_tables(self):
        """
        Creates tables for the defined models using the admin user.
        """
        try:
            db_name = Config.TEST_DB_NAME if self.test else Config.DB_NAME
            engine_with_db = create_engine(f"{self.admin_db_uri}{db_name}")
            print("Creating tables...")
            Base.metadata.create_all(engine_with_db)
            print("Tables created successfully.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating tables: {e}")

    def create_departments(self):
        """
        Creates unique departments using the admin user.
        """
        try:
            db_name = Config.TEST_DB_NAME if self.test else Config.DB_NAME
            engine_with_db = create_engine(f"{self.admin_db_uri}{db_name}")
            Session = sessionmaker(bind=engine_with_db)
            session = Session()

            departments = ["Commercial", "Support", "Gestion"]
            for dept_name in departments:
                existing_dept = session.query(Department).filter_by(name=dept_name).first()
                if not existing_dept:
                    department = Department(name=dept_name)
                    session.add(department)
            session.commit()
            print("Departments created successfully.")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating departments: {e}")

    def initialize(self):
        """
        Initialize the database by performing all necessary steps.
        """
        try:
            self.create_database()  # Create the database using the admin user
            self.create_user()  # Create user and grant necessary privileges
            self.create_tables()  # Create tables using the admin user
            self.create_departments()  # Create unique departments using the admin user
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Failed to initialize the database: {e}")
