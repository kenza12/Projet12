import pytest
from models.event import Event
from models.contract import Contract
from models.client import Client
from models.user import User
from datetime import datetime, date

def test_create_event(db_session):
    """Test the creation of an Event."""
    user = User(
        username="johndoe",
        password="password123",
        email="johndoe@example.com",
        name="John Doe"
    )
    db_session.add(user)
    db_session.commit()
    # print(f"User created: username={user.username}, email={user.email}, name={user.name}")

    client = Client(
        full_name="Alice Smith",
        email="alice@example.com",
        phone="+123456789",
        company_name="Alice's Adventures",
        date_created=date.today(),
        last_contact_date=date.today(),
        commercial_contact=user
    )
    db_session.add(client)
    db_session.commit()
    # print(f"Client created: full_name={client.full_name}, email={client.email}, company_name={client.company_name}")

    contract = Contract(
        client=client,
        commercial_contact=user,
        total_amount=10000.00,
        amount_due=5000.00,
        date_created=date.today(),
        signed=False
    )
    db_session.add(contract)
    db_session.commit()
    # print(f"Contract created: total_amount={contract.total_amount}, amount_due={contract.amount_due}")

    event = Event(
        contract=contract,
        client=client,
        event_name="Annual Meeting",
        event_date_start=datetime(2024, 6, 1, 9, 0, 0),
        event_date_end=datetime(2024, 6, 1, 17, 0, 0),
        support_contact=user,
        location="Conference Room 1",
        attendees=50,
        notes="Annual meeting for shareholders."
    )
    db_session.add(event)
    db_session.commit()
    # print(f"Event created: event_name={event.event_name}, location={event.location}")

    retrieved_event = db_session.query(Event).filter_by(event_name="Annual Meeting").first()
    # print(f"Retrieved event: event_name={retrieved_event.event_name}, client={retrieved_event.client.full_name}, support_contact={retrieved_event.support_contact.username}")
    assert retrieved_event is not None, "Event not found"
    assert retrieved_event.client.full_name == "Alice Smith"
    assert retrieved_event.support_contact.username == "johndoe"
