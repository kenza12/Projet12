import unittest
from models.event import Event
from models.client import Client
from models.contract import Contract
from base_test import BaseTest
from controllers.main_controller import MainController
from models.user import User
import os


class TestEvent(BaseTest):
    """
    TestEvent class performs integration tests for event-related operations in the EpicEvents application.
    This includes creating/updating events, ensuring that unauthorized users cannot create events, and retrieving event information.
    """

    def test_get_events(self):
        """
        Test the retrieval of all events.
        This test covers the creation of a client, contract, and event,
        followed by the verification that the event is correctly stored
        and can be retrieved.
        """

        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client
        result = MainController.create_client(
            full_name="Get Events Test Client",
            email="geteventstestclient@example.com",
            phone="1234567890",
            company_name="Get Events Company"
        )
        print("Create client result:", result)
        self.assertIn("Client created successfully.", result, "Failed to create client")
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="geteventstestclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Reopen session
        self.reopen_session()

        # Authenticate as a management user to create a contract
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Create a new contract as management user
        result = MainController.create_contract(
            client_id=client_id,
            total_amount=11000.0,
            amount_due=6000.0,
            signed=True
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

        # Authenticate as the original commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new event
        result = MainController.create_event(
            contract_id=contract_id,
            event_name="Get Events Test Event",
            event_date_start="2024-07-02 10:00:00",
            event_date_end="2024-07-02 12:00:00",
            location="Get Events Location",
            attendees=200,
            notes="This is another test event"
        )
        print("Create event result:", result)
        self.assertIn("Event created successfully.", result, "Failed to create event")
        self.session.commit()

        # Retrieve all events
        events = MainController.get_events()
        self.assertTrue(len(events) > 0, "No events found")

        # Verify the specific event in the retrieved events
        event_names = [event.event_name for event in events]
        self.assertIn("Get Events Test Event", event_names, "Test event not found in the retrieved events")

    def test_update_event_assign_support_contact(self):
        """
        Test updating an event to assign a support contact by the management team.
        """
        # Authenticate as a commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new client
        result = MainController.create_client(
            full_name="Update Event Test Client",
            email="updateeventtestclient@example.com",
            phone="1234567890",
            company_name="Update Event Company"
        )
        print("Create client result:", result)
        self.assertIn("Client created successfully.", result, "Failed to create client")
        self.session.commit()

        # Verify that the client was created
        client = self.session.query(Client).filter_by(email="updateeventtestclient@example.com").first()
        self.assertIsNotNone(client, "Client not found in the database")
        client_id = client.id

        # Reopen session
        self.reopen_session()

        # Authenticate as a management user to create a contract
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Create a new contract as management user
        result = MainController.create_contract(
            client_id=client_id,
            total_amount=15000.0,
            amount_due=8000.0,
            signed=True
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

        # Authenticate as the original commercial user
        self.authenticate_user(os.getenv("USER1_USERNAME"), os.getenv("USER1_PASSWORD"))

        # Create a new event
        result = MainController.create_event(
            contract_id=contract_id,
            event_name="Update Event Test Event",
            event_date_start="2024-07-02 14:00:00",
            event_date_end="2024-07-02 16:00:00",
            location="Update Event Location",
            attendees=150,
            notes="This is a test event for updating"
        )
        print("Create event result:", result)
        self.assertIn("Event created successfully.", result, "Failed to create event")
        self.session.commit()

        # Verify that the event was created
        event = self.session.query(Event).filter_by(event_name="Update Event Test Event").first()
        self.assertIsNotNone(event, "Event not found in the database")
        event_id = event.id

        # Reopen session
        self.reopen_session()

        # Authenticate as a management user to update the event
        self.authenticate_user(os.getenv("USER3_USERNAME"), os.getenv("USER3_PASSWORD"))

        # Use the existing support user jane_support
        support_user = self.session.query(User).filter_by(username=os.getenv("USER2_USERNAME")).first()
        self.assertIsNotNone(support_user, "Support user not found in the database")
        support_user_id = support_user.id

        # Update the event to assign the support contact
        update_result = MainController.update_event(
            event_id=event_id,
            support_contact_id=support_user_id
        )
        print("Update event result:", update_result)
        self.assertIn("Event updated successfully.", update_result, "Failed to update event")
        self.session.commit()

        # Reopen session
        self.reopen_session()

        # Verify that the event was updated with the support contact
        updated_event = self.session.query(Event).filter_by(id=event_id).first()
        self.assertIsNotNone(updated_event.support_contact_id, "Support contact not assigned to the event")
        self.assertEqual(updated_event.support_contact_id, support_user_id, "Incorrect support contact assigned to the event")

if __name__ == '__main__':
    unittest.main()
