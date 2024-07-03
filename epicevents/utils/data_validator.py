from datetime import datetime
import re
from rich.console import Console
from controllers.user_controller import UserController

console = Console()

class DataValidator:
    """
    Validates the input data before processing it in the database.
    """

    @staticmethod
    def validate_string(value: str, field_name: str) -> bool:
        """
        Validates that a string is not empty and has at least 1 character.
        """
        if not value or not value.strip():
            console.print(f"[bold red]{field_name} cannot be empty.[/bold red]")
            return False
        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validates the email format.
        """
        email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not email or not re.match(email_regex, email):
            console.print("[bold red]Invalid email format.[/bold red]")
            return False
        return True

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validates the phone number format.
        """
        phone_regex = r'^\+?[0-9\s]*$'
        if not phone or not re.match(phone_regex, phone):
            console.print("[bold red]Invalid phone number format.[/bold red]")
            return False
        return True

    @staticmethod
    def validate_id(value: str, field_name: str) -> bool:
        """
        Validates that the ID is a positive integer.
        """
        try:
            if int(value) > 0:
                return True
            else:
                console.print(f"[bold red]{field_name} must be a positive integer.[/bold red]")
                return False
        except ValueError:
            console.print(f"[bold red]{field_name} must be a valid integer.[/bold red]")
            return False


    @staticmethod
    def validate_attendees(value: str, field_name: str) -> bool:
        """
        Validates that the attendees count is at least 1 and not negative.
        """
        try:
            attendees = int(value)
            if attendees > 0:
                return True
            else:
                console.print(f"[bold red]{field_name} must be at least 1.[/bold red]")
                return False
        except ValueError:
            console.print(f"[bold red]{field_name} must be a valid integer.[/bold red]")
            return False

    @staticmethod
    def validate_existing_user_id(value: str, field_name: str) -> bool:
        """
        Validates that the user ID exists in the database.
        """
        try:
            user_id = int(value)
            if user_id > 0 and UserController.user_exists(user_id):
                return True
            else:
                console.print(f"[bold red]{field_name} does not exist.[/bold red]")
                return False
        except ValueError:
            console.print(f"[bold red]{field_name} must be a valid integer.[/bold red]")
            return False

    @staticmethod
    def validate_department_id(value: str, field_name: str) -> bool:
        """
        Validates that the department ID is either 1, 2, or 3.
        """
        try:
            department_id = int(value)
            if department_id in [1, 2, 3]:
                return True
            else:
                console.print(f"[bold red]{field_name} must be 1, 2, or 3.[/bold red]")
                return False
        except ValueError:
            console.print(f"[bold red]{field_name} must be a valid integer.[/bold red]")
            return False

    @staticmethod
    def validate_float(value: str, field_name: str, positive: bool = True) -> bool:
        """
        Validates that a value is a float, optionally positive.
        """
        try:
            if positive and float(value) <= 0:
                console.print(f"[bold red]{field_name} must be a positive number.[/bold red]")
                return False
            elif not positive and float(value) < 0:
                console.print(f"[bold red]{field_name} cannot be negative.[/bold red]")
                return False
            return True
        except ValueError:
            console.print(f"[bold red]{field_name} must be a valid number.[/bold red]")
            return False

    @staticmethod
    def validate_datetime(datetime_text: str, field_name: str, start_datetime: str = None) -> bool:
        """
        Validates the date and time format (YYYY-MM-DD HH:MM:SS) and checks if the date is valid.
        Ensures the start date is not in the past and the end date is not before the start date.
        """
        try:
            dt = datetime.strptime(datetime_text, '%Y-%m-%d %H:%M:%S')
            if field_name == "Event Date Start" and dt < datetime.now():
                console.print("[bold red]Event Date Start cannot be in the past.[/bold red]")
                return False
            if field_name == "Event Date End" and start_datetime:
                start_dt = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
                if dt < start_dt:
                    console.print("[bold red]Event Date End cannot be before Event Date Start.[/bold red]")
                    return False
            return True
        except ValueError:
            console.print(f"[bold red]Invalid datetime format for {field_name}. Use YYYY-MM-DD HH:MM:SS.[/bold red]")
            return False

    @staticmethod
    def validate_boolean(value: str, field_name: str) -> bool:
        """
        Validates that the value is either 'true' or 'false'.
        """
        if value.lower() in ['true', 'false']:
            return True
        console.print(f"[bold red]{field_name} must be 'True' or 'False'.[/bold red]")
        return False

    @staticmethod
    def prompt_and_validate(prompt: str, validator_func, field_name: str = None, allow_empty: bool = False, **kwargs) -> str:
        """
        Prompt the user for input and validate it using the specified validator function.
        """
        while True:
            value = input(prompt).strip()
            if allow_empty and not value:
                return ""
            if field_name:
                if validator_func(value, field_name, **kwargs):
                    return value
            else:
                if validator_func(value, **kwargs):
                    return value
