import click
from rich.console import Console
from controllers.main_controller import MainController

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
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password of the user')
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

def start_cli():
    cli()

if __name__ == "__main__":
    cli()
