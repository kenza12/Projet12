import unittest
from models.client import Client
from base_test import BaseTest
from controllers.main_controller import MainController
import os
import pexpect
import sys
from config import Config


class TestClient(BaseTest):
    """
    TestClient class performs integration tests for client-related operations in the EpicEvents application.
    This includes creating clients, ensuring that unauthorized users cannot create clients, and updating client information.
    """

    def test_create_client_as_commercial(self):
        """Test creating a client as a commercial user."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

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
        self.reopen_session()

        # Verify that the client was created in the database
        client = self.session.query(Client).filter_by(email="testclient1@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        self.assertEqual(client.full_name, "Test Client 1")
        self.assertEqual(client.phone, "1234567890")
        self.assertEqual(client.company_name, "Test Company")

    def test_create_client_as_support_should_fail(self):
        """Test creating a client as a support user should fail."""

        # Authenticate as a support user
        self.authenticate_user(os.getenv("USER2_USERNAME"), os.getenv("USER2_PASSWORD"))

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
        self.reopen_session()

        # Verify that the client was not created in the database
        client = self.session.query(Client).filter_by(email="testclient2@example.com").first()
        self.assertIsNone(client, "Client should not be found in the database")

    def test_update_client_as_commercial(self):
        """Test updating a client as a commercial user."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

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
        self.reopen_session()

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
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

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
        self.authenticate_user(os.getenv("USER2_USERNAME"), os.getenv("USER2_PASSWORD"))

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
        self.reopen_session()

        # Verify that the client was not updated in the database
        not_updated_client = self.session.query(Client).filter_by(id=client_id).first()
        self.assertIsNotNone(not_updated_client, "Client not found in the database")
        self.assertEqual(not_updated_client.full_name, "Existing Client")
        self.assertEqual(not_updated_client.email, "anotherexistingclient@example.com")
        self.assertEqual(not_updated_client.phone, "1234567890")
        self.assertEqual(not_updated_client.company_name, "Existing Company")

    def test_create_client_interaction(self):
        """Test creating a client with user interaction validation using Pexpect."""

        # Obtenir le chemin de l'exécutable Python
        python_path = sys.executable

        # Ajouter le répertoire racine du projet à PYTHONPATH
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        os.environ['PYTHONPATH'] = project_root

        # Démarrer le processus interactif
        print("Starting the interactive process...")
        child = pexpect.spawn(f'{python_path} epicevents/main.py login --test', encoding='utf-8')

        # Activer le journal de débogage
        child.logfile = sys.stdout

        # Attendez l'invite de commande pour l'authentification et authentifiez-vous
        print("Expecting 'Username:' prompt...")
        child.expect('Username:')
        print("Sending username...")
        child.sendline(os.getenv("USER1_USERNAME"))
        
        print("Expecting 'Password:' prompt...")
        child.expect('Password:')
        print("Sending password...")
        child.sendline(os.getenv("USER1_PASSWORD"))

        # Attendez que l'utilisateur soit authentifié
        print("Expecting 'Authentication successful' message...")
        child.expect('Authentication successful', timeout=10)

        # Sélectionnez l'option pour gérer les clients
        print("Expecting 'Enter your choice:' prompt...")
        child.expect('Enter your choice:', timeout=10)
        print("Sending choice '1' for managing clients...")
        child.sendline('1')  # Choisir l'option pour gérer les clients

        # Sélectionnez l'option pour créer un client
        print("Expecting 'Enter your choice:' prompt...")
        child.expect('Enter your choice:', timeout=10)
        print("Sending choice '1' for creating a client...")
        child.sendline('1')  # Choisir l'option pour créer un client

        # Remplir les champs requis pour la création du client
        print("Expecting 'Full Name:' prompt...")
        child.expect('Full Name:', timeout=10)
        print("Sending full name...")
        child.sendline('Test Client Interaction')
        
        print("Expecting 'Email:' prompt...")
        child.expect('Email:', timeout=10)
        print("Sending email...")
        child.sendline('interactionclient@example.com')
        
        print("Expecting 'Phone:' prompt...")
        child.expect('Phone:', timeout=10)
        print("Sending phone number...")
        child.sendline('1234567890')
        
        print("Expecting 'Company Name:' prompt...")
        child.expect('Company Name:', timeout=10)
        print("Sending company name...")
        child.sendline('Interaction Company')

        # Attendez le résultat de la création du client
        print("Expecting 'Client created successfully.' message...")
        child.expect('Client created successfully.', timeout=10)

        # Vérifiez que le client a été créé dans la base de données
        print("Verifying client creation in the database...")
        self.session.commit()
        self.reopen_session()
        
        client = self.session.query(Client).filter_by(email='interactionclient@example.com').first()
        self.assertIsNotNone(client, "Client not found in the database")
        self.assertEqual(client.full_name, "Test Client Interaction")
        self.assertEqual(client.phone, "1234567890")
        self.assertEqual(client.company_name, "Interaction Company")

if __name__ == '__main__':
    unittest.main()
