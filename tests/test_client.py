import unittest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from config import Config
from utils.database_initializer import DatabaseInitializer
from controllers.main_controller import MainController
from models.user import User
from models.client import Client
from models.department import Department
import os


class TestClientIntegration(unittest.TestCase):
    """
    TestClientIntegration class performs integration tests for client-related operations in the EpicEvents application.
    This includes creating clients, ensuring that unauthorized users cannot create clients, and updating client information.
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
        self.engine = create_engine(Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD))
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

    def test_create_client_as_commercial(self):
        """Test creating a client as a commercial user."""

        # Authenticate as a commercial user
        tokens_commercial = MainController.authenticate(
            os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))
        assert tokens_commercial is not None, "Authentication failed for commercial user"

        # Attempt to create a new client
        result = MainController.create_client(
            full_name="Test Client 1",
            email="testclient1@example.com",
            phone="1234567890",
            company_name="Test Company"
        )
        print("Create client result:", result)
        self.assertIn("successfully", result, "Failed to create client")

        # Commit the transaction and close the session to ensure data is saved
        self.session.commit()
        self.session.close()

        # Reopen the session to check the database content
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.session = self.Session(bind=self.connection)

        # Verify that the client was created in the database
        client = self.session.query(Client).filter_by(email="testclient1@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        self.assertEqual(client.full_name, "Test Client 1")
        self.assertEqual(client.phone, "1234567890")
        self.assertEqual(client.company_name, "Test Company")

    def test_create_client_as_support_should_fail(self):
        """Test creating a client as a support user should fail."""

        # Authenticate as a support user
        tokens_support = MainController.authenticate(
            os.getenv("USER2_USERNAME"), os.getenv("USER2_PASSWORD"))
        assert tokens_support is not None, "Authentication failed for support user"

        # Attempt to create a new client (should fail)
        result = MainController.create_client(
            full_name="Test Client 2",
            email="testclient2@example.com",
            phone="1234567890",
            company_name="Test Company"
        )
        print("Create client result:", result)
        self.assertEqual(result, "You are not authorized to perform this action.", "Support user should not be authorized to create a client")

        # Commit the transaction and close the session to ensure data is saved
        self.session.commit()
        self.session.close()

        # Reopen the session to check the database content
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.session = self.Session(bind=self.connection)

        # Verify that the client was not created in the database
        client = self.session.query(Client).filter_by(email="testclient2@example.com").first()
        self.assertIsNone(client, "Client should not be found in the database")

    def test_update_client_as_commercial(self):
        """Test updating a client as a commercial user."""

        # Authenticate as a commercial user
        tokens_commercial = MainController.authenticate(
            os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))
        assert tokens_commercial is not None, "Authentication failed for commercial user"

        # Create a new client
        MainController.create_client(
            full_name="Existing Client",
            email="existingclient@example.com",
            phone="1234567890",
            company_name="Existing Company"
        )
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="existingclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Attempt to update the client
        result = MainController.update_client(
            client_id=client_id,
            full_name="Jane Doe",
            email="jane.doe@example.com",
            phone="0987654321",
            company_name="Doe Enterprises"
        )
        print("Update client result:", result)
        self.assertEqual(result, "Client updated successfully.", "Failed to update client as commercial user")

        # Commit the transaction and close the session to ensure data is saved
        self.session.commit()
        self.session.close()

        # Reopen the session to check the database content
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.session = self.Session(bind=self.connection)

        # Verify that the client was updated in the database
        updated_client = self.session.query(Client).filter_by(id=client_id).first()
        self.assertIsNotNone(updated_client, "Updated client not found in the database")
        self.assertEqual(updated_client.full_name, "Jane Doe")
        self.assertEqual(updated_client.email, "jane.doe@example.com")
        self.assertEqual(updated_client.phone, "0987654321")
        self.assertEqual(updated_client.company_name, "Doe Enterprises")

    def test_update_client_as_support_should_fail(self):
        """Test updating a client as a support user should fail."""

        # Authenticate as a commercial user
        tokens_commercial = MainController.authenticate(
            os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))
        assert tokens_commercial is not None, "Authentication failed for commercial user"

        # Create a new client
        MainController.create_client(
            full_name="Existing Client",
            email="anotherexistingclient@example.com",
            phone="1234567890",
            company_name="Existing Company"
        )
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="anotherexistingclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Authenticate as a support user
        tokens_support = MainController.authenticate(
            os.getenv("USER2_USERNAME"), os.getenv("USER2_PASSWORD"))
        assert tokens_support is not None, "Authentication failed for support user"

        # Attempt to update the client (should fail)
        result = MainController.update_client(
            client_id=client_id,
            full_name="Jane Doe",
            email="jane.doe2@example.com",
            phone="0987654321",
            company_name="Doe Enterprises"
        )
        print("Update client result:", result)
        self.assertEqual(result, "You are not authorized to perform this action.", "Support user should not be authorized to update a client")

        # Commit the transaction and close the session to ensure data is saved
        self.session.commit()
        self.session.close()

        # Reopen the session to check the database content
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.session = self.Session(bind=self.connection)

        # Verify that the client was not updated in the database
        not_updated_client = self.session.query(Client).filter_by(id=client_id).first()
        self.assertIsNotNone(not_updated_client, "Client not found in the database")
        self.assertEqual(not_updated_client.full_name, "Existing Client")
        self.assertEqual(not_updated_client.email, "anotherexistingclient@example.com")
        self.assertEqual(not_updated_client.phone, "1234567890")
        self.assertEqual(not_updated_client.company_name, "Existing Company")

    # def test_update_client_as_different_commercial_should_fail(self):
    #     """Test updating a client as a different commercial user should fail."""

    #     # Authenticate as the first commercial user
    #     tokens_commercial1 = MainController.authenticate(
    #         os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))
    #     assert tokens_commercial1 is not None, "Authentication failed for the first commercial user"

    #     # Create a new client
    #     MainController.create_client(
    #         full_name="Test Client 3",
    #         email="testclient3@example.com",
    #         phone="1234567890",
    #         company_name="Test Company 3"
    #     )
    #     self.session.commit()

    #     # Verify that the client was created
    #     client = self.session.query(Client).filter_by(email="testclient3@example.com").first()
    #     self.assertIsNotNone(client, "Client not found in the database")
    #     client_id = client.id

    #     # Authenticate as a management user
    #     tokens_management = MainController.authenticate(
    #         os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))
    #     assert tokens_management is not None, "Authentication failed for management user"

    #     # Ensure the department for the new commercial user exists
    #     department_id = self.session.query(Department).filter_by(name="Commercial").first().id
    #     assert department_id is not None, "Commercial department does not exist"

    #     # Create another commercial user
    #     MainController.create_collaborator(
    #         username="new_commercial",
    #         password="new_password",
    #         email="new_commercial@example.com",
    #         name="New Commercial",
    #         department_id=department_id  # Use the correct department ID
    #     )
    #     self.session.commit()

    #     # Authenticate as the second commercial user
    #     tokens_commercial2 = MainController.authenticate(
    #         "new_commercial", "new_password")
    #     assert tokens_commercial2 is not None, "Authentication failed for the second commercial user"

    #     # Patch the authentication and user inputs
    #     with patch('views.client_views.DataValidator.prompt_and_validate', side_effect=[client_id, "Updated Client", "updatedclient@example.com", "0987654321", "Updated Company"]), \
    #          patch('views.client_views.MainController.verify_authentication_and_authorization', return_value=(tokens_commercial2, tokens_commercial2, True)), \
    #          patch('views.client_views.ClientController.get_commercial_contact_id', return_value=tokens_commercial1['id']):

    #         # Attempt to update the client as the second commercial user (should fail)
    #         result = update_client()
    #         print("Update client result:", result)
    #         self.assertEqual(result, "You are not authorized to update this client.", "Second commercial user should not be authorized to update a client they are not responsible for")

    #     # Commit the transaction and close the session to ensure data is saved
    #     self.session.commit()
    #     self.session.close()

    #     # Reopen the session to check the database content
    #     self.connection = self.engine.connect()
    #     self.transaction = self.connection.begin()
    #     self.session = self.Session(bind=self.connection)

    #     # Verify that the client was not updated in the database
    #     not_updated_client = self.session.query(Client).filter_by(id=client_id).first()
    #     self.assertIsNotNone(not_updated_client, "Client not found in the database")
    #     self.assertEqual(not_updated_client.full_name, "Test Client 3")
    #     self.assertEqual(not_updated_client.email, "testclient3@example.com")
    #     self.assertEqual(not_updated_client.phone, "1234567890")
    #     self.assertEqual(not_updated_client.company_name, "Test Company 3")

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

if __name__ == '__main__':
    unittest.main()
