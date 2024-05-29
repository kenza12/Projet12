import pytest
from models.user import User
from models.department import Department

def test_create_user(db_session):
    """Test the creation of a User."""
    department = Department(name="Sales")
    db_session.add(department)
    db_session.commit()
    # print(f"Department created: name={department.name}")

    user = User(
        username="johndoe",
        password="password123",
        email="johndoe@example.com",
        name="John Doe",
        department=department
    )
    db_session.add(user)
    db_session.commit()
    # print(f"User created: username={user.username}, email={user.email}, name={user.name}, department={user.department.name}")

    retrieved_user = db_session.query(User).filter_by(username="johndoe").first()
    # print(f"Retrieved user: username={retrieved_user.username}, email={retrieved_user.email}, department={retrieved_user.department.name}")
    assert retrieved_user is not None, "User not found"
    assert retrieved_user.email == "johndoe@example.com"
    assert retrieved_user.department.name == "Sales"
