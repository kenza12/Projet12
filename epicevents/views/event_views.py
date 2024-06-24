from rich.console import Console
from controllers.main_controller import MainController
from controllers.client_controller import ClientController
from controllers.user_controller import UserController
from controllers.contract_controller import ContractController
from utils.table_printer import print_table


console = Console()


def get_events():
    """
    Retrieve and display all events if the user is authenticated and authorized.
    """
    events = MainController.get_events()
    if events:
        event_data = [{
            "Event ID": event.id,
            "Contract ID": event.contract_id,
            "Client ID": event.client_id,
            "Event Name": event.event_name,
            "Start Date": event.event_date_start,
            "End Date": event.event_date_end,
            "Support Contact ID": event.support_contact_id if event.support_contact_id else "None",
            "Location": event.location,
            "Attendees": event.attendees,
            "Notes": event.notes
        } for event in events]
        
        print_table(event_data, title="Events")
    else:
        console.print("[bold red]No events found or you are not authorized to view them.[/bold red]")


def create_event_commercial():
    try:
        contract_id = int(input("Contract ID: "))
        
        # Vérification du contrat
        contract = ContractController.get_contract_by_id(contract_id)
        if not contract:
            console.print("[bold red]Contract not found.[/bold red]")
            return

        if not contract.signed:
            console.print("[bold red]The contract is not signed.[/bold red]")
            return
        
        current_username = MainController.get_current_user()
        current_user_id = UserController.get_user_id_by_username(current_username)
        
        if contract.commercial_contact_id != current_user_id:
            console.print("[bold red]You are not authorized to create an event for this contract.[/bold red]")
            return

        event_name = input("Event Name: ")
        event_date_start = input("Event Date Start (YYYY-MM-DD HH:MM:SS): ")
        event_date_end = input("Event Date End (YYYY-MM-DD HH:MM:SS): ")
        location = input("Location: ")
        attendees = int(input("Attendees: "))
        notes = input("Notes: ")
        
        result_message = MainController.create_event(contract_id, event_name, event_date_start, event_date_end, location, attendees, notes)
        console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")
    except ValueError as ve:
        console.print(f"[bold red]Input Error: {ve}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


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
        event_date_start = input("Event Date Start (YYYY-MM-DD HH:MM:SS, leave blank to skip): ").strip() or None
        event_date_end = input("Event Date End (YYYY-MM-DD HH:MM:SS, leave blank to skip): ").strip() or None
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


def filter_events():
    """
    Filter events based on criteria.
    """
    username = MainController.get_current_user()
    user_role = MainController.get_user_role(username)

    while True:
        console.print("[bold blue]Filter Events[/bold blue]")
        if user_role == "Support":
            console.print("1. Events Assigned to Me\n2. Events by Client\n3. Events by Date Range\n4. Events by Location\n5. Events by Attendance\n6. Return to Main Menu")
        elif user_role == "Gestion":
            console.print("1. Events with No Support Contact\n2. Events by Client\n3. Events by Date Range\n4. Events by Location\n5. Events by Attendance\n6. Return to Main Menu")

        choice = input("Enter your choice: ")
        filters = {}

        if user_role == "Support" and choice == '1':
            current_username = MainController.get_current_user()
            current_user_id = UserController.get_user_id_by_username(current_username)
            filters['support_contact_id'] = current_user_id
        elif choice == '1':
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