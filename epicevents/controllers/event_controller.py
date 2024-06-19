from models.event import Event
from models.user import User
import sentry_sdk
from utils.token_manager import TokenManager
from utils.session_manager import get_session
from utils.data_validator import DataValidator
from sqlalchemy import func


class EventController:
    @staticmethod
    def get_all_events(token: str) -> list:
        """
        Retrieves all events if the user is authenticated and authorized.
        Args:
            token (str): JWT token of the authenticated user.
        Returns:
            list: List of Event objects.
        """
        try:
            key = TokenManager.load_key()
            payload = TokenManager.verify_token(token, key)
            if payload:
                session = get_session()
                events = session.query(Event).all()
                return events
            return []
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []

    @staticmethod
    def create_event(contract_id: int, client_id: int, event_name: str, event_date_start: str, event_date_end: str,
                     support_contact_id: int, location: str, attendees: int, notes: str) -> bool:
        """
        Creates a new event if data is valid.
        """
        try:
            session = get_session()
            if not (DataValidator.validate_datetime(event_date_start) and DataValidator.validate_datetime(event_date_end)):
                raise ValueError("Invalid date provided for creating event.")

            event = Event(contract_id=contract_id, client_id=client_id, event_name=event_name, event_date_start=event_date_start,
                          event_date_end=event_date_end, support_contact_id=support_contact_id, location=location,
                          attendees=attendees, notes=notes)
            session.add(event)
            session.commit()
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            session.rollback()
            return False

    @staticmethod
    def update_event(token: str, user: User, event_id: int, contract_id: int = None, client_id: int = None, event_name: str = None,
                     event_date_start: str = None, event_date_end: str = None, support_contact_id: int = None, location: str = None,
                     attendees: int = None, notes: str = None) -> bool:
        """
        Updates an existing event if data is valid.
        """
        try:
            session = get_session()
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                raise ValueError("Event not found.")

            if support_contact_id is not None:
                event.support_contact_id = support_contact_id

            if user.department.name == "Support":
                if contract_id is not None:
                    event.contract_id = contract_id
                if client_id is not None:
                    event.client_id = client_id
                if event_name and DataValidator.validate_not_empty(event_name):
                    event.event_name = event_name
                if event_date_start and DataValidator.validate_date(event_date_start):
                    event.event_date_start = event_date_start
                if event_date_end and DataValidator.validate_date(event_date_end):
                    event.event_date_end = event_date_end
                if location:
                    event.location = location
                if attendees:
                    event.attendees = attendees
                if notes:
                    event.notes = notes

            session.commit()
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

    @staticmethod
    def get_filtered_events(filters: dict) -> list:
        """
        Retrieves events based on specified filters.
        Args:
            filters (dict): Dictionary of filters.
        Returns:
            list: List of Event objects that match the filters.
        """
        try:
            session = get_session()
            query = session.query(Event)
            if 'no_support' in filters and filters['no_support']:
                query = query.filter(Event.support_contact_id.is_(None))
            if 'client_id' in filters:
                query = query.filter(Event.client_id == filters['client_id'])
            if 'date_start' in filters:
                date_start = filters['date_start']
                query = query.filter(func.date(Event.event_date_start) >= date_start)
            if 'date_end' in filters:
                date_end = filters['date_end']
                query = query.filter(func.date(Event.event_date_end) <= date_end)
            if 'location' in filters:
                query = query.filter(Event.location == filters['location'])
            if 'min_attendees' in filters:
                query = query.filter(Event.attendees >= filters['min_attendees'])
            if 'max_attendees' in filters:
                query = query.filter(Event.attendees <= filters['max_attendees'])
            return query.all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []