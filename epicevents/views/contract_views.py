from rich.console import Console
from controllers.main_controller import MainController
from utils.table_printer import print_table

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
        signed_input = input("Signed (True/False, leave blank to skip): ").strip().lower()
        signed = None
        if signed_input:
            signed = signed_input == 'true'
        
        result_message = MainController.update_contract(contract_id, client_id if client_id else None, float(total_amount) if total_amount else None, float(amount_due) if amount_due else None, signed)
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