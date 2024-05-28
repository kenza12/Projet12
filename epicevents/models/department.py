from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config import Base


class Department(Base):
    """
    Represents a department in the Epic Events CRM.

    Attributes:
        id (int): Unique identifier for the department.
        name (str): Name of the department.
    """
    __tablename__ = 'Department'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    users = relationship("User", back_populates="department", cascade="all, delete")