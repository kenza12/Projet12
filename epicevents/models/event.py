from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config import Base


class Event(Base):
    """
    Represents an event in the Epic Events CRM.

    Attributes:
        id (int): Unique identifier for the event.
        contract_id (int): Foreign key referencing the Contract.
        client_id (int): Foreign key referencing the Client.
        event_name (str): Name of the event.
        event_date_start (datetime): Start date and time of the event.
        event_date_end (datetime): End date and time of the event.
        support_contact_id (int): Foreign key referencing the User (support contact).
        location (str): Location of the event.
        attendees (int): Number of attendees for the event.
        notes (str): Additional notes for the event.
    """
    __tablename__ = 'Event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey('Contract.id', ondelete='CASCADE'), nullable=False)
    client_id = Column(Integer, ForeignKey('Client.id', ondelete='CASCADE'), nullable=True)
    event_name = Column(String(100), nullable=False)
    event_date_start = Column(DateTime, nullable=False)
    event_date_end = Column(DateTime, nullable=False)
    support_contact_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'), nullable=True)
    location = Column(String(200), nullable=True)
    attendees = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    client = relationship("Client", back_populates="events")
    contract = relationship("Contract", back_populates="events")
    support_contact = relationship("User", back_populates="events")