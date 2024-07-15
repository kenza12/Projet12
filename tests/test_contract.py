import unittest
from models.contract import Contract
from models.client import Client
from models.department import Department
from base_test import BaseTest
from controllers.main_controller import MainController
import os


class TestContract(BaseTest):
    """
    TestContract class performs integration tests for contract-related operations in the EpicEvents application.
    This includes creating contracts, ensuring that unauthorized users cannot create contracts, and updating contract information.
    """

    def test_create_contract_as_management(self):
        """Test creating a contract as a management user."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client as a commercial user
        result = MainController.create_client(
            full_name="Commercial Test Client",
            email="commercialclient@example.com",
            phone="1234567890",
            company_name="Commercial Company",
        )
        print("Create client result:", result)
        self.session.commit()
        self.assertIn("Client created successfully.", result, "Failed to create client")

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="commercialclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Authenticate as a management user
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Create a new contract
        result = MainController.create_contract(
            client_id=client_id, total_amount=5000.0, amount_due=2500.0, signed=True
        )
        print("Create contract result:", result)
        self.assertIn("successfully", result, "Failed to create contract")

        # Commit the transaction and close the session to ensure data is saved
        self.session.commit()
        self.reopen_session()

        # Verify that the contract was created in the database
        contract = self.session.query(Contract).filter_by(client_id=client_id).first()
        self.assertIsNotNone(contract, "Contract not found in the database")
        self.assertEqual(contract.total_amount, 5000.0)
        self.assertEqual(contract.amount_due, 2500.0)
        self.assertTrue(contract.signed)

    def test_update_contract_as_management(self):
        """Test updating a contract as a management user."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client as a commercial user
        result = MainController.create_client(
            full_name="Commercial Update Client",
            email="commercialupdateclient@example.com",
            phone="1234567890",
            company_name="Management Update Company",
        )
        print("Create client result:", result)
        self.assertIn("Client created successfully.", result, "Failed to create client")
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="commercialupdateclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Reopen session
        self.reopen_session()

        # Authenticate as a management user
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Create a new contract
        result = MainController.create_contract(
            client_id=client_id, total_amount=6000.0, amount_due=3000.0, signed=False
        )
        print("Create contract result:", result)
        self.assertIn("Contract created successfully.", result, "Failed to create contract")
        self.session.commit()

        # Verify that the contract was created
        contract = self.session.query(Contract).filter_by(client_id=client_id).first()
        self.assertIsNotNone(contract, "Contract not found in the database")
        contract_id = contract.id

        # Reopen session
        self.reopen_session()

        # Update the contract
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))
        result = MainController.update_contract(
            contract_id=contract_id, total_amount=6500.0, amount_due=3500.0, signed=True
        )
        print("Update contract result:", result)
        self.assertIn("Contract updated successfully.", result, "Failed to update contract")
        self.session.commit()

        # Reopen the session to check the database content
        self.reopen_session()

        # Verify that the contract was updated in the database
        updated_contract = self.session.query(Contract).filter_by(id=contract_id).first()
        self.assertIsNotNone(updated_contract, "Updated contract not found in the database")
        self.assertEqual(updated_contract.total_amount, 6500.0)
        self.assertEqual(updated_contract.amount_due, 3500.0)
        self.assertTrue(updated_contract.signed)

    def test_create_contract_as_commercial_should_fail(self):
        """Test creating a contract as a commercial user."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client
        result = MainController.create_client(
            full_name="Commercial Test Client",
            email="commercialclient_john@example.com",
            phone="1234567890",
            company_name="Commercial Company",
        )
        print("Create client result:", result)
        self.assertIn("successfully", result, "Failed to create client")
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="commercialclient_john@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Attempt to create a new contract (should fail)
        result = MainController.create_contract(
            client_id=client_id, total_amount=7000.0, amount_due=3500.0, signed=True
        )
        print("Create contract result:", result)
        self.assertIn(
            "You are not authorized to perform this action.",
            result,
            "Commercial user should not be authorized to create a contract",
        )

        # Verify that the contract was not created in the database
        contract = self.session.query(Contract).filter_by(client_id=client_id).first()
        self.assertIsNone(contract, "Contract should not be found in the database")

    def test_update_contract_as_commercial(self):
        """Test updating a contract as a commercial user."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client
        result = MainController.create_client(
            full_name="Commercial Update Client",
            email="commercialupdateclient@example.com",
            phone="1234567890",
            company_name="Commercial Update Company",
        )
        print("Create client result:", result)
        self.assertIn("successfully", result, "Failed to create client")
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="commercialupdateclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Reopen session
        self.reopen_session()

        # Re-authenticate as a management user to create a contract
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Create a new contract as management user
        result = MainController.create_contract(
            client_id=client_id, total_amount=8000.0, amount_due=4000.0, signed=False
        )
        print("Create contract result:", result)
        self.assertIn("successfully", result, "Failed to create contract")
        self.session.commit()

        # Verify that the contract was created
        contract = self.session.query(Contract).filter_by(client_id=client_id).first()
        self.assertIsNotNone(contract, "Contract not found in the database")
        contract_id = contract.id

        # Reopen session
        self.reopen_session()

        # Re-authenticate as the original commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Update the contract as the original commercial user
        result = MainController.update_contract(
            contract_id=contract_id, total_amount=8500.0, amount_due=4500.0, signed=True
        )
        print("Update contract result:", result)
        self.assertIn("successfully", result, "Failed to update contract")
        self.session.commit()

        # Reopen session
        self.reopen_session()

        # Verify that the contract was updated in the database
        updated_contract = self.session.query(Contract).filter_by(id=contract_id).first()
        self.assertIsNotNone(updated_contract, "Updated contract not found in the database")
        self.assertEqual(updated_contract.total_amount, 8500.0)
        self.assertEqual(updated_contract.amount_due, 4500.0)
        self.assertTrue(updated_contract.signed)

    def test_update_contract_as_different_commercial_should_fail(self):
        """Test updating a contract as a different commercial user should fail."""

        # Authenticate as the first commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client
        result = MainController.create_client(
            full_name="Test Client 3",
            email="testclient3@example.com",
            phone="1234567890",
            company_name="Test Company 3",
        )
        print("Create client result:", result)
        self.assertIn("successfully", result, "Failed to create client")
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="testclient3@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Reopen session
        self.reopen_session()

        # Authenticate as a management user to create a contract
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Create a new contract as management user
        result = MainController.create_contract(
            client_id=client_id, total_amount=8000.0, amount_due=4000.0, signed=False
        )
        print("Create contract result:", result)
        self.assertIn("successfully", result, "Failed to create contract")
        self.session.commit()

        # Verify that the contract was created
        contract = self.session.query(Contract).filter_by(client_id=client_id).first()
        self.assertIsNotNone(contract, "Contract not found in the database")
        contract_id = contract.id

        # Ensure the department for the new commercial user exists
        department_id = self.session.query(Department).filter_by(name="Commercial").first().id
        assert department_id is not None, "Commercial department does not exist"

        # Create another commercial user with management user
        result = MainController.create_collaborator(
            username="new_commercial",
            password="new_password",
            email="new_commercial@example.com",
            name="New Commercial",
            department_id=department_id,  # Use the correct department ID
        )
        print("Create collaborator result:", result)
        self.assertIn("Collaborator created successfully.", result, "Failed to create collaborator")
        self.session.commit()

        # Re-authenticate as the second commercial user
        self.authenticate_user("new_commercial", "new_password")

        # Update the contract as the second commercial user (should fail)
        result = MainController.update_contract(
            contract_id=contract_id, total_amount=8500.0, amount_due=4500.0, signed=True
        )
        print("Update contract result:", result)
        self.assertIn(
            "You are not authorized to update this contract.",
            result,
            "Second commercial user should not be authorized to update a contract they are not responsible for",
        )
        self.session.commit()

        # Reopen session
        self.reopen_session()

        # Verify that the contract was not updated in the database
        not_updated_contract = self.session.query(Contract).filter_by(id=contract_id).first()
        self.assertIsNotNone(not_updated_contract, "Contract not found in the database")
        self.assertEqual(not_updated_contract.total_amount, 8000.0)
        self.assertEqual(not_updated_contract.amount_due, 4000.0)
        self.assertFalse(not_updated_contract.signed)

    def test_get_contracts(self):
        """Test retrieving all contracts."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client
        result = MainController.create_client(
            full_name="Get Contracts Test Client",
            email="getcontractstestclient@example.com",
            phone="1234567890",
            company_name="Get Contracts Company",
        )
        print("Create client result:", result)
        self.assertIn("successfully", result, "Failed to create client")
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="getcontractstestclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Reopen session
        self.reopen_session()

        # Authenticate as a management user to create a contract
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Create a new contract as management user
        result = MainController.create_contract(
            client_id=client_id, total_amount=9000.0, amount_due=5000.0, signed=True
        )
        print("Create contract result:", result)
        self.assertIn("successfully", result, "Failed to create contract")
        self.session.commit()

        # Retrieve all contracts
        contracts = MainController.get_contracts()
        self.assertTrue(len(contracts) > 0, "No contracts found")

    def test_filter_contracts(self):
        """Test filtering contracts as a commercial user."""

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client
        result = MainController.create_client(
            full_name="Filter Contracts Test Client",
            email="filtercontractstestclient@example.com",
            phone="1234567890",
            company_name="Filter Contracts Company",
        )
        print("Create client result:", result)
        self.assertIn("Client created successfully.", result, "Failed to create client")
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="filtercontractstestclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Reopen session
        self.reopen_session()

        # Authenticate as a management user to create contracts
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Create a signed contract
        result = MainController.create_contract(client_id=client_id, total_amount=5000.0, amount_due=0.0, signed=True)
        print("Create signed contract result:", result)
        self.assertIn("Contract created successfully.", result, "Failed to create signed contract")
        self.session.commit()
        self.reopen_session()

        # Create an unsigned contract
        result = MainController.create_contract(
            client_id=client_id, total_amount=6000.0, amount_due=6000.0, signed=False
        )
        print("Create unsigned contract result:", result)
        self.assertIn("Contract created successfully.", result, "Failed to create unsigned contract")
        self.session.commit()
        self.reopen_session()

        # Create a partially paid contract
        result = MainController.create_contract(
            client_id=client_id, total_amount=7000.0, amount_due=3500.0, signed=True
        )
        print("Create partially paid contract result:", result)
        self.assertIn("Contract created successfully.", result, "Failed to create partially paid contract")
        self.session.commit()
        self.reopen_session()

        # Re-authenticate as a commercial user to filter contracts
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Filter unsigned contracts
        try:
            filters = {"signed": False}
            contracts = MainController.filter_contracts(filters)
            print("Unsigned contracts:", contracts)  # Log the contracts
            self.assertTrue(len(contracts) > 0, "No unsigned contracts found")
            for contract in contracts:
                self.assertFalse(contract.signed, "Found a signed contract in unsigned contracts filter")
        except PermissionError as e:
            self.fail(f"Permission error: {e}")

        # Reopen session before the next filter
        self.reopen_session()

        # Filter unpaid contracts
        try:
            filters = {"unpaid": True}
            contracts = MainController.filter_contracts(filters)
            print("Unpaid contracts:", contracts)  # Log the contracts
            self.assertTrue(len(contracts) > 0, "No unpaid contracts found")
            for contract in contracts:
                self.assertGreater(contract.amount_due, 0, "Found a fully paid contract in unpaid contracts filter")
        except PermissionError as e:
            self.fail(f"Permission error: {e}")


if __name__ == "__main__":
    unittest.main()
