from rich.console import Console
from controllers.main_controller import MainController
from controllers.client_controller import ClientController
from utils.table_printer import print_table
from utils.data_validator import DataValidator

console = Console()


def create_contract():
    """
    Prompt the user for details to create a new contract.
    """
    try:
        client_name = DataValidator.prompt_and_validate("Client Name: ", DataValidator.validate_string, "Client Name")
        client_id = ClientController.get_client_id_by_name(client_name)
        if not client_id:
            console.print("[bold red]Client not found.[/bold red]")
            return
        
        total_amount = DataValidator.prompt_and_validate("Total Amount: ", DataValidator.validate_float, "Total Amount")
        console.print("[bold blue]If there is no amount due, enter 0.[/bold blue]")
        amount_due = DataValidator.prompt_and_validate("Amount Due: ", lambda value: DataValidator.validate_float(value, "Amount Due", False, True))
        signed = DataValidator.prompt_and_validate("Signed (True/False): ", DataValidator.validate_boolean, "Signed").lower() == 'true'

        result_message = MainController.create_contract(int(client_id), float(total_amount), float(amount_due), signed)
        console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")
    except ValueError as ve:
        console.print(f"[bold red]Input Error: {ve}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


def update_contract():
    """
    Prompt the user for details to update an existing contract.
    """
    try:
        contract_id = DataValidator.prompt_and_validate("Contract ID: ", DataValidator.validate_id, "Contract ID")
        client_id = DataValidator.prompt_and_validate("Client ID (leave blank to skip): ", DataValidator.validate_id, "Client ID", allow_empty=True)
        total_amount = DataValidator.prompt_and_validate("Total Amount (leave blank to skip): ", DataValidator.validate_float, "Total Amount", allow_empty=True)
        amount_due = DataValidator.prompt_and_validate("Amount Due (leave blank to skip): ", DataValidator.validate_float, "Amount Due", allow_empty=True, positive=False)
        signed_input = DataValidator.prompt_and_validate("Signed (True/False, leave blank to skip): ", DataValidator.validate_boolean, "Signed", allow_empty=True)
        signed = signed_input.lower() == 'true' if signed_input else None

        update_data = {}
        if client_id:
            update_data["client_id"] = int(client_id)
        if total_amount:
            update_data["total_amount"] = float(total_amount)
        if amount_due:
            update_data["amount_due"] = float(amount_due)
        if signed is not None:
            update_data["signed"] = signed

        result_message = MainController.update_contract(contract_id, **update_data)
        console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")
    except ValueError as ve:
        console.print(f"[bold red]Input Error: {ve}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


def get_contracts():
    """
    Retrieve and display all contracts if the user is authenticated and authorized.
    """
    contracts = MainController.get_contracts()
    if contracts:
        contract_data = [{
            "Contract ID": contract.id,
            "Client ID": contract.client_id,
            "Commercial Contact ID": contract.commercial_contact_id,
            "Total Amount": contract.total_amount,
            "Amount Due": contract.amount_due,
            "Date Created": contract.date_created,
            "Signed": contract.signed
        } for contract in contracts]
        
        print_table(contract_data, title="Contracts")
    else:
        console.print("[bold red]No contracts found or you are not authorized to view them.[/bold red]")


def filter_contracts():
    console.print("[bold blue]Filter Contracts[/bold blue]")
    console.print("1. Unsigned Contracts\n2. Unpaid Contracts\n3. Return to Main Menu")
    choice = input("Enter your choice: ")
    
    filters = {}
    if choice == '1':
        filters['signed'] = False
    elif choice == '2':
        filters['unpaid'] = True
    elif choice == '3':
        return
    else:
        console.print("[bold red]Invalid choice. Please try again.[/bold red]")
        return

    contracts = MainController.filter_contracts(filters)
    if contracts:
        contract_data = [{
            "Contract ID": contract.id,
            "Client ID": contract.client_id,
            "Total Amount": contract.total_amount,
            "Amount Due": contract.amount_due,
            "Signed": contract.signed
        } for contract in contracts]
        
        print_table(contract_data, title="Filtered Contracts")
    else:
        console.print("[bold red]No contracts found matching the criteria.[/bold red]")
