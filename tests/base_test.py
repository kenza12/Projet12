import unittest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from config import Config
from utils.database_initializer import DatabaseInitializer
from controllers.main_controller import MainController


class BaseTest(unittest.TestCase):
    """
    BaseTest class provides common setup, teardown, and utility methods for integration tests.
    """

    def setUp(self):
        """Set up before each test method."""
        # Use the test database
        MainController.set_use_test_database(True)

        # Initialize the database
        db_initializer = DatabaseInitializer()
        db_initializer.initialize()
        print("Database initialized.")

        # Create a new session
        self.engine = create_engine(Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD, test=True))
        self.Session = sessionmaker(bind=self.engine)

        # Create users for testing
        self.create_users()

        # Start a new transaction
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.session = self.Session(bind=self.connection)

    def create_users(self):
        """Create users for testing."""
        session = self.Session()
        try:
            MainController.create_users()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def authenticate_user(self, username, password):
        """Authenticate a user and return tokens."""
        tokens = MainController.authenticate(username, password)
        assert tokens is not None, f"Authentication failed for user {username}"
        return tokens

    def reopen_session(self):
        """Close and reopen the session to ensure it is updated."""
        self.session.close()
        self.connection.close()
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.session = self.Session(bind=self.connection)

    def tearDown(self):
        """Tear down after each test method."""
        # Roll back the session and close the transaction and connection
        self.session.rollback()
        self.session.close()
        self.transaction.rollback()
        self.connection.close()

        # Clean up the database
        self.clear_database()

    def clear_database(self):
        """Clear all tables in the database."""
        # Reflect the database schema and delete all data from each table
        meta = MetaData()
        meta.reflect(bind=self.engine)
        with self.engine.begin() as conn:
            for table in reversed(meta.sorted_tables):
                conn.execute(table.delete())
