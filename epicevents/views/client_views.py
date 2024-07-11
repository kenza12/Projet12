from rich.console import Console
from controllers.main_controller import MainController
from controllers.client_controller import ClientController
from utils.table_printer import print_table
from utils.data_validator import DataValidator

console = Console()


def create_client():
    """
    Prompt the user for details to create a new client.
    """
    full_name = DataValidator.prompt_and_validate("Full Name: ", DataValidator.validate_string, "Full Name")
    email = DataValidator.prompt_and_validate("Email: ", DataValidator.validate_email)
    phone = DataValidator.prompt_and_validate("Phone: ", DataValidator.validate_phone)
    company_name = DataValidator.prompt_and_validate("Company Name: ", DataValidator.validate_string, "Company Name")

    data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company_name": company_name
    }

    result_message = MainController.create_client(**data)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")
    print ("*************CREATE_CLIENT********************")


def update_client():
    """
    Prompt the user for details to update an existing client.
    """
    client_id = DataValidator.prompt_and_validate("Client ID: ", DataValidator.validate_id, "Client ID")

    # Retrieve the commercial contact ID for the client
    commercial_contact_id = ClientController.get_commercial_contact_id(client_id)
    if commercial_contact_id is None:
        console.print("[bold red]Client not found.[/bold red]")
        return
    
    # Verify if the user is authorized to update the client
    token, user, authorized = MainController.verify_authentication_and_authorization('update_client')
    if authorized and user.id != commercial_contact_id:
        console.print("[bold red]You are not authorized to update this client.[/bold red]")
        return

    full_name = DataValidator.prompt_and_validate("New Full Name (leave blank to skip): ", DataValidator.validate_string, "Full Name", allow_empty=True)
    email = DataValidator.prompt_and_validate("New Email (leave blank to skip): ", DataValidator.validate_email, allow_empty=True)
    phone = DataValidator.prompt_and_validate("New Phone (leave blank to skip): ", DataValidator.validate_phone, allow_empty=True)
    company_name = DataValidator.prompt_and_validate("New Company Name (leave blank to skip): ", DataValidator.validate_string, "Company Name", allow_empty=True)

    update_data = {}
    if full_name:
        update_data["full_name"] = full_name
    if email:
        update_data["email"] = email
    if phone:
        update_data["phone"] = phone
    if company_name:
        update_data["company_name"] = company_name

    result_message = MainController.update_client(client_id, **update_data)
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
