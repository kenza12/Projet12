from rich.console import Console
from controllers.main_controller import MainController

console = Console()


def create_collaborator():
    """
    Prompt the user for details to create a new collaborator.
    """
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email: ")
    name = input("Name: ")

    console.print("[bold blue]Departments:[/bold blue]")
    console.print("+----+------------+")
    console.print("| id | name       |")
    console.print("+----+------------+")
    console.print("|  1 | Commercial |")
    console.print("|  2 | Support    |")
    console.print("|  3 | Gestion    |")
    console.print("+----+------------+")

    department_id = int(input("Department ID: "))

    result_message = MainController.create_collaborator(username, password, email, name, department_id)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")


def update_collaborator():
    """
    Prompt the user for details to update an existing collaborator.
    """
    try:
        user_id = int(input("User ID: "))
        username = input("Username (leave blank to skip): ")
        password = input("Password (leave blank to skip): ")
        email = input("Email (leave blank to skip): ")
        name = input("Name (leave blank to skip): ")

        console.print("[bold blue]Departments:[/bold blue]")
        console.print("+----+------------+")
        console.print("| id | name       |")
        console.print("+----+------------+")
        console.print("|  1 | Commercial |")
        console.print("|  2 | Support    |")
        console.print("|  3 | Gestion    |")
        console.print("+----+------------+")

        department_id = input("Department ID (leave blank to skip): ")
        
        department_id = int(department_id) if department_id else None
        
        result_message = MainController.update_collaborator(user_id, username, password, email, name, department_id)
        console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")
    except ValueError as ve:
        console.print(f"[bold red]Input Error: {ve}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


def delete_collaborator():
    """
    Prompt the user for the ID of the collaborator to be deleted.
    """
    user_id = int(input("User ID: "))
    result_message = MainController.delete_collaborator(user_id)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")
