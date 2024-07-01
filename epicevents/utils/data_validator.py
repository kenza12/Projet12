from datetime import datetime
import re


class DataValidator:
    """
    Validates the input data before processing it in the database.
    """

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validates the email format.
        """
        email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.match(email_regex, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validates the phone number format.
        """
        phone_regex = r'^\+?[0-9\s]*$'
        return re.match(phone_regex, phone) is not None

    @staticmethod
    def validate_datetime(datetime_text: str) -> bool:
        """
        Validates the date and time format (YYYY-MM-DD HH:MM:SS).
        """
        try:
            datetime.strptime(datetime_text, '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_not_empty(value: str) -> bool:
        """
        Validates that the value is not empty.
        """
        return bool(value and value.strip())
