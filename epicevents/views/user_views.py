from rich.console import Console
from controllers.main_controller import MainController
from utils.data_validator import DataValidator

console = Console()


def create_collaborator():
    """
    Prompt the user for details to create a new collaborator.
    """
    username = DataValidator.prompt_and_validate("Username: ", DataValidator.validate_string, "Username")
    password = DataValidator.prompt_and_validate("Password: ", DataValidator.validate_string, "Password")
    email = DataValidator.prompt_and_validate("Email: ", DataValidator.validate_email)
    name = DataValidator.prompt_and_validate("Name: ", DataValidator.validate_string, "Name")

    console.print("[bold blue]Departments:[/bold blue]")
    console.print("+----+------------+")
    console.print("| id | name       |")
    console.print("+----+------------+")
    console.print("|  1 | Commercial |")
    console.print("|  2 | Support    |")
    console.print("|  3 | Gestion    |")
    console.print("+----+------------+")

    department_id = DataValidator.prompt_and_validate(
        "Department ID: ", DataValidator.validate_department_id, "Department ID"
    )

    result_message = MainController.create_collaborator(username, password, email, name, int(department_id))
    console.print(
        f"[bold green]{result_message}[/bold green]"
        if "successfully" in result_message
        else f"[bold red]{result_message}[/bold red]"
    )


def update_collaborator():
    """
    Prompt the user for details to update an existing collaborator.
    """
    try:
        user_id = DataValidator.prompt_and_validate("User ID: ", DataValidator.validate_existing_user_id, "User ID")
        username = DataValidator.prompt_and_validate(
            "Username (leave blank to skip): ", DataValidator.validate_string, "Username", allow_empty=True
        )
        password = DataValidator.prompt_and_validate(
            "Password (leave blank to skip): ", DataValidator.validate_string, "Password", allow_empty=True
        )
        email = DataValidator.prompt_and_validate(
            "Email (leave blank to skip): ", DataValidator.validate_email, allow_empty=True
        )
        name = DataValidator.prompt_and_validate(
            "Name (leave blank to skip): ", DataValidator.validate_string, "Name", allow_empty=True
        )

        console.print("[bold blue]Departments:[/bold blue]")
        console.print("+----+------------+")
        console.print("| id | name       |")
        console.print("+----+------------+")
        console.print("|  1 | Commercial |")
        console.print("|  2 | Support    |")
        console.print("|  3 | Gestion    |")
        console.print("+----+------------+")

        department_id = (
            DataValidator.prompt_and_validate(
                "Department ID (leave blank to skip): ",
                DataValidator.validate_department_id,
                "Department ID",
                allow_empty=True,
            )
            or None
        )

        update_data = {}
        if username:
            update_data["username"] = username
        if password:
            update_data["password"] = password
        if email:
            update_data["email"] = email
        if name:
            update_data["name"] = name
        if department_id:
            update_data["department_id"] = int(department_id)

        result_message = MainController.update_collaborator(int(user_id), **update_data)
        console.print(
            f"[bold green]{result_message}[/bold green]"
            if "successfully" in result_message
            else f"[bold red]{result_message}[/bold red]"
        )
    except ValueError as ve:
        console.print(f"[bold red]Input Error: {ve}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


def delete_collaborator():
    """
    Prompt the user for the ID of the collaborator to be deleted.
    """
    user_id = DataValidator.prompt_and_validate("User ID: ", DataValidator.validate_existing_user_id, "User ID")
    result_message = MainController.delete_collaborator(int(user_id))
    console.print(
        f"[bold green]{result_message}[/bold green]"
        if "successfully" in result_message
        else f"[bold red]{result_message}[/bold red]"
    )
