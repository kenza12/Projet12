from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config import Base


class Contract(Base):
    """
    Represents a contract in the Epic Events CRM.

    Attributes:
        id (int): Unique identifier for the contract.
        client_id (int): Foreign key referencing the Client.
        commercial_contact_id (int): Foreign key referencing the User (commercial contact).
        total_amount (float): Total amount of the contract.
        amount_due (float): Amount due for the contract.
        date_created (date): Date when the contract was created.
        signed (bool): Indicates whether the contract is signed.
    """

    __tablename__ = "Contract"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("Client.id", ondelete="CASCADE"), nullable=True)
    commercial_contact_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=True)
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    date_created = Column(Date, nullable=False)
    signed = Column(Boolean, nullable=False, default=False)

    client = relationship("Client", back_populates="contracts")
    commercial_contact = relationship("User", back_populates="contracts")
    events = relationship("Event", back_populates="contract", cascade="all, delete")
