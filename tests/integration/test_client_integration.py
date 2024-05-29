import pytest
from models.client import Client
from models.user import User
from datetime import date

def test_create_client(db_session):
    """Test the creation of a Client."""
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

    retrieved_client = db_session.query(Client).filter_by(email="alice@example.com").first()
    # print(f"Retrieved client: {retrieved_client.full_name}, {retrieved_client.email}, {retrieved_client.commercial_contact.username}")
    assert retrieved_client is not None, "Client not found"
    assert retrieved_client.full_name == "Alice Smith"
    assert retrieved_client.commercial_contact.username == "johndoe"
