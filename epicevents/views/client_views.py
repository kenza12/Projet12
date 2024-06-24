from rich.console import Console
from controllers.main_controller import MainController
from utils.table_printer import print_table

console = Console()


def create_client():
    full_name = input("Full Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    company_name = input("Company Name: ")
    result_message = MainController.create_client(full_name, email, phone, company_name)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")


def update_client():
    client_name = input("Client Name: ")
    full_name = input("New Full Name (leave blank to skip): ")
    email = input("New Email (leave blank to skip): ")
    phone = input("New Phone (leave blank to skip): ")
    company_name = input("New Company Name (leave blank to skip): ")
    result_message = MainController.update_client(client_name, full_name, email, phone, company_name)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")


def get_clients():
    """
    Retrieve and display all clients if the user is authenticated and authorized.
    """
    clients = MainController.get_clients()
    if clients:
        client_data = [{
            "Client ID": client.id,
            "Full Name": client.full_name,
            "Email": client.email,
            "Phone": client.phone,
            "Company Name": client.company_name,
            "Date Created": client.date_created,
            "Last Contact Date": client.last_contact_date,
            "Commercial Contact ID": client.commercial_contact_id
        } for client in clients]
        
        print_table(client_data, title="Clients")
    else:
        console.print("[bold red]No clients found or you are not authorized to view them.[/bold red]")
