import click
from rich.console import Console
from controllers.main_controller import MainController

console = Console()

def create_client():
    full_name = input("Full Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    company_name = input("Company Name: ")
    result_message = MainController.create_client(full_name, email, phone, company_name)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")

def update_client():
    client_id = input("Client ID: ")
    full_name = input("Full Name (leave blank to skip): ")
    email = input("Email (leave blank to skip): ")
    phone = input("Phone (leave blank to skip): ")
    company_name = input("Company Name (leave blank to skip): ")
    last_contact_date = input("Last Contact Date (YYYY-MM-DD, leave blank to skip): ")
    result_message = MainController.update_client(client_id, full_name, email, phone, company_name, last_contact_date)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")

def get_clients():
    """
    Retrieve and display all clients if the user is authenticated and authorized.
    """
    clients = MainController.get_clients()
    if clients:
        for client in clients:
            console.print(f"Client: {client.full_name}, Email: {client.email}")
    else:
        console.print("[bold red]No clients found or you are not authorized to view them.[/bold red]")
