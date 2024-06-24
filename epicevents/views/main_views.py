import click
from rich.console import Console
from controllers.main_controller import MainController
from views.client_views import create_client, update_client, get_clients
from views.user_views import create_collaborator, update_collaborator, delete_collaborator
from views.contract_views import create_contract, update_contract, get_contracts, filter_contracts
from views.event_views import get_events, update_event, filter_events, create_event_commercial

console = Console()

@click.group()
def cli():
    """Epic Events CRM Command Line Interface"""
    pass

@cli.command()
def initialize():
    """
    Initialize the database and create initial users.
    """
    try:
        if not MainController.initialize_database():
            console.print("[bold red]Error during database initialization. Check logs for details.[/bold red]")
            return

        if not MainController.create_users():
            console.print("[bold red]Error during user creation. Check logs for details.[/bold red]")
            return

        console.print("[bold green]Database initialized and users created successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error during initialization: {e}[/bold red]")

@cli.command()
@click.option('--username', prompt='Username', help='The username of the user')
@click.option('--password', prompt=True, hide_input=True, help='The password of the user')
def login(username, password):
    """
    Authenticate a user and generate JWT and refresh tokens.
    """
    if not MainController.is_database_initialized():
        console.print("[bold red]Database is not initialized. Please run 'initialize' first.[/bold red]")
        return

    tokens = MainController.authenticate(username, password)
    if tokens:
        console.print(f"Authentication successful. Your tokens have been stored.", style="bold green")
        display_menu()  # Call the display_menu function after successful login
    else:
        console.print("[bold red]Authentication failed.[/bold red]")

@cli.command()
@click.option('--username', prompt='Username', help='The username of the user')
@click.option('--password', prompt=True, hide_input=True, help='The password of the user')
def refresh(username, password):
    """
    Refresh the JWT token using the refresh token.
    """
    new_token = MainController.refresh_token(username, password)
    if new_token:
        console.print(f"Token refreshed successfully. Your new token has been stored.", style="bold green")
    else:
        console.print("[bold red]Failed to refresh token. No active session found, please login first.[/bold red]")

@cli.command()
@click.option('--username', prompt='Username', help='The username of the user')
def check_token(username):
    """
    Check the token status and inform the user if it needs to be refreshed.
    """
    result = MainController.check_token_status(username)
    if result == "expired":
        console.print("[bold red]Your session has expired. Please refresh your token by running `python epicevents/main.py refresh --username <username>`.[/bold red]")
    elif result == "active":
        console.print("[bold green]Your session is active.[/bold green]")
    else:
        console.print("[bold red]No valid token found. Please log in by running `python epicevents/main.py login`.[/bold red]")

@cli.command()
def logout():
    """
    Logout the user by deleting the JWT token.
    """
    result = MainController.logout()
    if result == "logged_out":
        console.print("[bold green]You have been logged out.[/bold green]")
    elif result == "no_session":
        console.print("[bold red]No active session found.[/bold red]")
    else:
        console.print(f"[bold red]Error during logout: {result}[/bold red]")

def display_menu():
    """
    Display the user-specific menu based on the user's role.
    """
    username = MainController.get_current_user()
    user_role = MainController.get_user_role(username)
    
    if user_role == 'Commercial':
        commercial_menu()
    elif user_role == 'Support':
        support_menu()
    elif user_role == 'Gestion':
        gestion_menu()
    else:
        console.print("[bold red]Unknown role. Cannot display menu.[/bold red]")

def commercial_menu():
    """
    Display the menu for the Commercial department.
    """
    while True:
        console.print("[bold blue]Commercial Menu[/bold blue]")
        console.print("1. Manage Clients\n2. Manage Contracts\n3. Manage Events\n4. List All\n5. Logout\n6. Quit")
        choice = input("Enter your choice: ")
        if choice == '1':
            manage_clients()
        elif choice == '2':
            manage_contracts()
        elif choice == '3':
            manage_events_commercial()
        elif choice == '4':
            list_all()
        elif choice == '5':
            MainController.logout()
            return
        elif choice == '6':
            exit()
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def support_menu():
    """
    Display the menu for the Support department.
    """
    while True:
        console.print("[bold blue]Support Menu[/bold blue]")
        console.print("1. Manage Events\n2. List All\n3. Logout\n4. Quit")
        choice = input("Enter your choice: ")
        if choice == '1':
            manage_events_support()
        elif choice == '2':
            list_all()
        elif choice == '3':
            MainController.logout()
            return
        elif choice == '4':
            exit()
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def manage_events_support():
    """
    Submenu for managing events for the Support department.
    """
    while True:
        console.print("[bold blue]Support Event Management[/bold blue]")
        console.print("1. Filter Events\n2. Update Event\n3. Return to Main Menu")
        choice = input("Enter your choice: ")
        if choice == '1':
            filter_events()
        elif choice == '2':
            update_event()
        elif choice == '3':
            return
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def gestion_menu():
    """
    Display the menu for the Gestion department.
    """
    while True:
        console.print("[bold blue]Gestion Menu[/bold blue]")
        console.print("1. Manage Collaborators\n2. Manage Contracts\n3. Manage Events\n4. List All\n5. Logout\n6. Quit")
        choice = input("Enter your choice: ")
        if choice == '1':
            manage_collaborators()
        elif choice == '2':
            manage_contracts()
        elif choice == '3':
            manage_events_gestion()
        elif choice == '4':
            list_all()
        elif choice == '5':
            MainController.logout()
            return
        elif choice == '6':
            exit()
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def manage_clients():
    """
    Submenu for managing clients.
    """
    while True:
        console.print("[bold blue]Client Management[/bold blue]")
        console.print("1. Create Client\n2. Update Client\n3. Return to Main Menu")
        choice = input("Enter your choice: ")
        if choice == '1':
            create_client()
        elif choice == '2':
            update_client()
        elif choice == '3':
            return
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def manage_contracts():
    """
    Submenu for managing contracts.
    """
    username = MainController.get_current_user()
    user_role = MainController.get_user_role(username)
    
    while True:
        console.print("[bold blue]Contract Management[/bold blue]")
        if user_role == "Gestion":
            console.print("1. Create Contract\n2. Update Contract\n3. Return to Main Menu")
        elif user_role == "Commercial":
            console.print("1. Update Contract\n2. Filter Contracts\n3. Return to Main Menu")
        choice = input("Enter your choice: ")
        if choice == '1':
            if user_role == "Gestion":
                create_contract()
            elif user_role == "Commercial":
                update_contract()
        elif choice == '2':
            if user_role == "Gestion":
                update_contract()
            elif user_role == "Commercial":
                filter_contracts()
        elif choice == '3':
            return
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def manage_events_commercial():
    """
    Submenu for managing events.
    """
    while True:
        console.print("[bold blue]Event Management[/bold blue]")
        console.print("1. Create Event\n2. Return to Main Menu")
        choice = input("Enter your choice: ")
        if choice == '1':
            create_event_commercial()
        elif choice == '2':
            return
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def manage_events_gestion():
    """
    Submenu for managing events for the Gestion department.
    """
    while True:
        console.print("[bold blue]Gestion Event Management[/bold blue]")
        console.print("1. Update Event Support Contact\n2. Filter Events\n3. Return to Main Menu")
        choice = input("Enter your choice: ")
        if choice == '1':
            update_event()
        elif choice == '2':
            filter_events()
        elif choice == '3':
            return
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def manage_collaborators():
    """
    Submenu for managing collaborators.
    """
    while True:
        console.print("[bold blue]Collaborator Management[/bold blue]")
        console.print("1. Create Collaborator\n2. Update Collaborator\n3. Delete Collaborator\n4. Return to Main Menu")
        choice = input("Enter your choice: ")
        if choice == '1':
            create_collaborator()
        elif choice == '2':
            update_collaborator()
        elif choice == '3':
            delete_collaborator()
        elif choice == '4':
            return
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def list_all():
    """
    Submenu for listing all clients, contracts, and events.
    """
    while True:
        console.print("[bold blue]List All[/bold blue]")
        console.print("1. List Clients\n2. List Contracts\n3. List Events\n4. Return to Main Menu")
        choice = input("Enter your choice: ")
        if choice == '1':
            get_clients()
        elif choice == '2':
            get_contracts()
        elif choice == '3':
            get_events()
        elif choice == '4':
            return
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def start_cli():
    cli()

if __name__ == "__main__":
    cli()
