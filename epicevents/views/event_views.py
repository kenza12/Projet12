from rich.console import Console
from controllers.main_controller import MainController
from controllers.client_controller import ClientController
from controllers.user_controller import UserController
from controllers.contract_controller import ContractController
from utils.table_printer import print_table
from utils.data_validator import DataValidator


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
    """
    Prompt the user for details to create a new event for commercial users.
    """
    try:
        contract_id = DataValidator.prompt_and_validate("Contract ID: ", DataValidator.validate_id, "Contract ID")
        
        # Vérification du contrat
        contract = ContractController.get_contract_by_id(int(contract_id))
        if not contract:
            console.print("[bold red]Contract not found.[/bold red]")
            return

        if not contract.signed:
            console.print("[bold red]The contract is not signed.[/bold red]")
            return
        
        current_user = MainController.get_current_user()
        current_user_id = UserController.get_user_id_by_username(current_user)
        
        if contract.commercial_contact_id != current_user_id:
            console.print("[bold red]You are not authorized to create an event for this contract.[/bold red]")
            return

        event_name = DataValidator.prompt_and_validate("Event Name: ", DataValidator.validate_string, "Event Name")
        event_date_start = DataValidator.prompt_and_validate("Event Date Start (YYYY-MM-DD HH:MM:SS): ", DataValidator.validate_datetime, "Event Date Start")
        event_date_end = DataValidator.prompt_and_validate("Event Date End (YYYY-MM-DD HH:MM:SS): ", DataValidator.validate_datetime, "Event Date End", start_datetime=event_date_start)
        location = DataValidator.prompt_and_validate("Location: ", DataValidator.validate_string, "Location")
        attendees = DataValidator.prompt_and_validate("Attendees: ", DataValidator.validate_attendees, "Attendees")
        notes = input("Notes: ").strip()  # Notes can be optional
        
        result_message = MainController.create_event(int(contract_id), event_name, event_date_start, event_date_end, location, int(attendees), notes)
        console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")
    except ValueError as ve:
        console.print(f"[bold red]Input Error: {ve}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def update_event():
    """
    Prompt the user for details to update an existing event for support and gestion teams.
    """
    username = MainController.get_current_user()
    user_role = MainController.get_user_role(username)

    event_id = DataValidator.prompt_and_validate("Event ID: ", DataValidator.validate_id, "Event ID")
    support_contact_id = None

    update_data = {}

    if user_role == "Support":
        contract_id = DataValidator.prompt_and_validate("Contract ID (leave blank to skip): ", DataValidator.validate_id, "Contract ID", allow_empty=True)
        client_id = DataValidator.prompt_and_validate("Client ID (leave blank to skip): ", DataValidator.validate_id, "Client ID", allow_empty=True)
        event_name = DataValidator.prompt_and_validate("Event Name (leave blank to skip): ", DataValidator.validate_string, "Event Name", allow_empty=True)
        event_date_start = DataValidator.prompt_and_validate("Event Date Start (YYYY-MM-DD HH:MM:SS, leave blank to skip): ", DataValidator.validate_datetime, "Event Date Start", allow_empty=True)
        event_date_end = DataValidator.prompt_and_validate("Event Date End (YYYY-MM-DD HH:MM:SS, leave blank to skip): ", DataValidator.validate_datetime, "Event Date End", allow_empty=True, start_datetime=event_date_start)
        location = DataValidator.prompt_and_validate("Location (leave blank to skip): ", DataValidator.validate_string, "Location", allow_empty=True)
        attendees = DataValidator.prompt_and_validate("Attendees (leave blank to skip): ", DataValidator.validate_attendees, "Attendees", allow_empty=True)
        notes = input("Notes (leave blank to skip): ").strip()

        if contract_id:
            update_data["contract_id"] = int(contract_id)
        if client_id:
            update_data["client_id"] = int(client_id)
        if event_name:
            update_data["event_name"] = event_name
        if event_date_start:
            update_data["event_date_start"] = event_date_start
        if event_date_end:
            update_data["event_date_end"] = event_date_end
        if location:
            update_data["location"] = location
        if attendees:
            update_data["attendees"] = int(attendees)
        if notes:
            update_data["notes"] = notes

    if user_role == "Gestion":
        support_contact_name = DataValidator.prompt_and_validate("Support Contact Name: ", DataValidator.validate_string, "Support Contact Name")
        support_contact_id = UserController.get_user_id_by_name(support_contact_name)
        if support_contact_id is None:
            console.print(f"[bold red]Support Contact '{support_contact_name}' not found.[/bold red]")
            return
        
        support_user = UserController.get_user_by_id(support_contact_id)
        if support_user is None:
            console.print(f"[bold red]Support Contact '{support_contact_name}' not found.[/bold red]")
            return
        
        support_user_role = MainController.get_user_role(support_user.username)
        if support_user_role != "Support":
            console.print(f"[bold red]User '{support_contact_name}' is not in the Support department.[/bold red]")
            return
        
        update_data["support_contact_id"] = int(support_contact_id)

    result_message = MainController.update_event(
        event_id,
        update_data.get("contract_id"),
        update_data.get("client_id"),
        update_data.get("event_name"),
        update_data.get("event_date_start"),
        update_data.get("event_date_end"),
        update_data.get("support_contact_id"),
        update_data.get("location"),
        update_data.get("attendees"),
        update_data.get("notes")
    )
    console.print(f"[bold green]{result_message}[/bold green]" if "successfully" in result_message else f"[bold red]{result_message}[/bold red]")


def filter_events():
    """
    Filter events based on criteria for support and gestion teams.
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
            current_user = MainController.get_current_user()
            current_user_id = UserController.get_user_id_by_username(current_user)
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
            
            print_table(event_data, title="Filtered Events")
        else:
            console.print("[bold red]No events found matching the criteria or you are not authorized to view them.[/bold red]")