import click
from rich.console import Console
from controllers.main_controller import MainController

console = Console()

def create_contract():
    try:
        client_id = int(input("Client ID: "))
        total_amount = float(input("Total Amount: "))
        amount_due = float(input("Amount Due: "))
        signed_input = input("Signed (True/False): ").strip().lower()
        signed = signed_input == 'true'
        
        print(f"Attempting to create contract with: client_id={client_id}, total_amount={total_amount}, amount_due={amount_due}, signed={signed}")
        result_message = MainController.create_contract(client_id, total_amount, amount_due, signed)
        console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")
    except ValueError as ve:
        console.print(f"[bold red]Input Error: {ve}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def update_contract():
    try:
        contract_id = int(input("Contract ID: "))
        client_id = input("Client ID (leave blank to skip): ")
        total_amount = input("Total Amount (leave blank to skip): ")
        amount_due = input("Amount Due (leave blank to skip): ")
        date_created = input("Date Created (YYYY-MM-DD, leave blank to skip): ")
        signed_input = input("Signed (True/False, leave blank to skip): ").strip().lower()
        signed = None
        if signed_input:
            signed = signed_input == 'true'
        
        commercial_contact_id = input("Commercial Contact ID (leave blank to skip): ")
        if commercial_contact_id:
            commercial_contact_id = int(commercial_contact_id)
        
        result_message = MainController.update_contract(contract_id, client_id if client_id else None, commercial_contact_id if commercial_contact_id else None, float(total_amount) if total_amount else None, float(amount_due) if amount_due else None, date_created if date_created else None, signed)
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
        for contract in contracts:
            console.print(f"Contract ID: {contract.id}, Client ID: {contract.client_id}, Total Amount: {contract.total_amount}")
    else:
        console.print("[bold red]No contracts found or you are not authorized to view them.[/bold red]")
