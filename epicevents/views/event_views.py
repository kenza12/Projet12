import click
from rich.console import Console
from controllers.main_controller import MainController
from controllers.client_controller import ClientController
from controllers.user_controller import UserController
from utils.table_printer import print_table


console = Console()

def get_events():
    """
    Retrieve and display all events if the user is authenticated and authorized.
    """
    events = MainController.get_events()
    if events:
        for event in events:
            console.print(f"Event: {event.event_name}, Location: {event.location}")
    else:
        console.print("[bold red]No events found or you are not authorized to view them.[/bold red]")

def update_event():
    """
    Update an event.
    """
    username = MainController.get_current_user()
    user_role = MainController.get_user_role(username)

    event_id = input("Event ID: ").strip()
    support_contact_id = None
    contract_id = client_id = event_name = event_date_start = event_date_end = location = attendees = notes = None

    if user_role == "Support":
        contract_id = input("Contract ID (leave blank to skip): ").strip() or None
        client_id = input("Client ID (leave blank to skip): ").strip() or None
        event_name = input("Event Name (leave blank to skip): ").strip() or None
        event_date_start = input("Event Date Start (YYYY-MM-DD, leave blank to skip): ").strip() or None
        event_date_end = input("Event Date End (YYYY-MM-DD, leave blank to skip): ").strip() or None
        location = input("Location (leave blank to skip): ").strip() or None
        attendees = input("Attendees (leave blank to skip): ").strip() or None
        notes = input("Notes (leave blank to skip): ").strip() or None

    if user_role == "Gestion":
        support_contact_name = input("Support Contact Name: ").strip()
        support_contact_id = UserController.get_user_id_by_name(support_contact_name)
        if support_contact_id is None:
            console.print(f"[bold red]Support Contact '{support_contact_name}' not found.[/bold red]")
            return

    result_message = MainController.update_event(event_id, contract_id, client_id, event_name, event_date_start, event_date_end, support_contact_id, location, attendees, notes)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")

def update_event_support_contact():
    """
    Update the support contact of an event.
    """
    event_id = input("Event ID: ").strip()
    support_contact_name = input("Support Contact Name: ").strip()

    support_contact_id = UserController.get_user_id_by_name(support_contact_name)
    if support_contact_id is None:
        console.print(f"[bold red]Support Contact '{support_contact_name}' not found.[/bold red]")
        return

    result_message = MainController.update_event(event_id, support_contact_id=support_contact_id)
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")


def filter_events():
    """
    Filter events based on criteria.
    """
    while True:
        console.print("[bold blue]Filter Events[/bold blue]")
        console.print("1. Events with No Support Contact\n2. Events by Client\n3. Events by Date Range\n4. Events by Location\n5. Events by Attendance\n6. Return to Main Menu")
        choice = input("Enter your choice: ")
        
        filters = {}
        if choice == '1':
            filters['no_support'] = True
        elif choice == '2':
            client_name = input("Enter Client Name: ").strip()
            if client_name:
                client_id = ClientController.get_client_id_by_name(client_name)
                if client_id:
                    filters['client_id'] = client_id
                else:
                    console.print(f"[bold red]Client '{client_name}' not found.[/bold red]")
                    continue
            else:
                console.print("[bold red]Client Name cannot be empty.[/bold red]")
                continue
        elif choice == '3':
            date_start = input("Enter Start Date (YYYY-MM-DD): ").strip()
            date_end = input("Enter End Date (YYYY-MM-DD): ").strip()
            if date_start and date_end:
                filters['date_start'] = date_start
                filters['date_end'] = date_end
            else:
                console.print("[bold red]Both Start Date and End Date must be provided.[/bold red]")
                continue
        elif choice == '4':
            location = input("Enter Location: ").strip()
            if location:
                filters['location'] = location
            else:
                console.print("[bold red]Location cannot be empty.[/bold red]")
                continue
        elif choice == '5':
            min_attendees = input("Enter Minimum Attendees: ").strip()
            max_attendees = input("Enter Maximum Attendees: ").strip()
            if min_attendees and max_attendees:
                try:
                    filters['min_attendees'] = int(min_attendees)
                    filters['max_attendees'] = int(max_attendees)
                except ValueError:
                    console.print("[bold red]Invalid values for attendance. Please enter numbers.[/bold red]")
                    continue
            else:
                console.print("[bold red]Both Minimum and Maximum Attendees must be provided.[/bold red]")
                continue
        elif choice == '6':
            return
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")
            continue

        events = MainController.filter_events(filters)
        if events:
            event_data = [{
                "Event Name": event.event_name,
                "Location": event.location,
                "Start Date": event.event_date_start,
                "End Date": event.event_date_end,
                "Support Contact ID": event.support_contact_id if event.support_contact_id else "None",
                "Attendees": event.attendees,
                "Notes": event.notes
            } for event in events]
            
            print_table(event_data, title="Filtered Events")
        else:
            console.print("[bold red]No events found matching the criteria or you are not authorized to view them.[/bold red]")
