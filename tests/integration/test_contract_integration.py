import pytest
from models.contract import Contract
from models.client import Client
from models.user import User
from datetime import date

def test_create_contract(db_session):
    """Test the creation of a Contract."""
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

    retrieved_contract = db_session.query(Contract).filter_by(total_amount=10000.00).first()
    # print(f"Retrieved contract: total_amount={retrieved_contract.total_amount}, client={retrieved_contract.client.full_name}, commercial_contact={retrieved_contract.commercial_contact.username}")
    assert retrieved_contract is not None, "Contract not found"
    assert retrieved_contract.client.full_name == "Alice Smith"
    assert retrieved_contract.commercial_contact.username == "johndoe"
