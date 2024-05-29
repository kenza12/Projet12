import pytest
from models.department import Department

def test_create_department(db_session):
    """Test the creation of a Department."""
    department = Department(name="Sales")
    db_session.add(department)
    db_session.commit()
    # print(f"Department created: {department}")

    retrieved_department = db_session.query(Department).filter_by(name="Sales").first()
    assert retrieved_department is not None, "Department not found"
    assert retrieved_department.name == "Sales"
