from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class User(Base):
    """
    Represents a user (employee) in the Epic Events CRM.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Unique username for the user.
        password (str): Password for the user.
        email (str): Unique email address of the user.
        name (str): Full name of the user.
        department_id (int): Foreign key referencing the Department.
    """
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    department_id = Column(Integer, ForeignKey('Department.id', ondelete='CASCADE'), nullable=True)

    department = relationship("Department", back_populates="users")
    clients = relationship("Client", back_populates="commercial_contact", cascade="all, delete")
    contracts = relationship("Contract", back_populates="commercial_contact", cascade="all, delete")
    events = relationship("Event", back_populates="support_contact", cascade="all, delete")