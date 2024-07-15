from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class Client(Base):
    """
    Represents a client in the Epic Events CRM.

    Attributes:
        id (int): Unique identifier for the client.
        full_name (str): Full name of the client.
        email (str): Unique email address of the client.
        phone (str): Phone number of the client.
        company_name (str): Name of the client's company.
        date_created (date): Date when the client was first contacted.
        last_contact_date (date): Date of the last contact with the client.
        commercial_contact_id (int): Foreign key referencing the User (commercial contact).
    """

    __tablename__ = "Client"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    company_name = Column(String(100), nullable=True)
    date_created = Column(Date, nullable=False)
    last_contact_date = Column(Date, nullable=True)
    commercial_contact_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=True)

    commercial_contact = relationship("User", back_populates="clients")
    contracts = relationship("Contract", back_populates="client", cascade="all, delete")
    events = relationship("Event", back_populates="client", cascade="all, delete")
