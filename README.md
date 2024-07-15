# EpicEvents

EpicEvents is a CRM (Customer Relationship Management) application designed to manage clients, contracts, and events for a company. The application uses a MySQL database for data storage and SQLAlchemy in Python for database interactions. It includes features for creating and managing clients, contracts, and events, along with user authentication via JWT tokens.

## Prerequisites

- Python 3.9 or higher
- MySQL Server
- Git
- Pipenv

## Installation

1. **Clone the Repository**

Clone the repository from GitHub to your local machine.

```sh
git clone https://github.com/kenza12/Projet12.git
cd Projet12
```

2. **Set Up a Virtual Environment**

It is recommended to use Pipenv to manage dependencies.

```sh
pipenv install
pipenv shell
```

3. **Configure Environment Variables**

The `.env` file is used to configure database connection parameters and other settings. Create a `.env` file in the root directory of the project and add the following configuration:

```code
# Name of the main database
DB_NAME=epicevents

# Name of the test database
TEST_DB_NAME=epicevents_test

# Host where the MySQL server is running
DB_HOST=localhost

# Port on which the MySQL server is listening
DB_PORT=3306

# MySQL root user credentials
ADMIN_DB_USER=root
ADMIN_DB_PASSWORD=your_root_password

# Non-privileged database user credentials
DB_USER=matt
DB_PASSWORD=your_user_password

# Sentry DSN for error tracking
SENTRY_DSN=your_sentry_dsn

# Initial test user 1 details
USER1_USERNAME=john_commercial
USER1_PASSWORD=password123
USER1_EMAIL=john_commercial@example.com
USER1_NAME=John Commercial
USER1_DEPARTMENT=Commercial

# Initial test user 2 details
USER2_USERNAME=jane_support
USER2_PASSWORD=password123
USER2_EMAIL=jane_support@example.com
USER2_NAME=Jane Support
USER2_DEPARTMENT=Support

# Initial test user 3 details
USER3_USERNAME=jack_gestion
USER3_PASSWORD=password123
USER3_EMAIL=jack_gestion@example.com
USER3_NAME=Jack Gestion
USER3_DEPARTMENT=Gestion
```

Make sure that `ADMIN_DB_USER` and `ADMIN_DB_PASSWORD` match your MySQL root user credentials.

To avoid exposing sensitive information, add your `.env` file to `.gitignore`.

4. **Prepare the Database**

Before running the script, make sure your MySQL server is running.

```sh
sudo systemctl start mysql  # On Linux systems
```

5. **Initialize the Database**

Run the following command to initialize the database and create the initial users:

```sh
python epicevents/main.py initialize
```

6. **Run the CLI**

Use the CLI commands to manage the application:

- **login:**

Use this command to authenticate a user. You will be prompted to enter a username and password. If the authentication is successful, JWT and refresh tokens will be generated and stored securely.

```sh
python epicevents/main.py login
```

- **Refresh Token:**

```sh
python epicevents/main.py refresh
```

This command allows you to refresh the JWT token using a valid refresh token. You will be prompted to enter a username and password. If the provided refresh token is valid, a new JWT token will be generated and stored.

- **Check Token Status:**

```sh
python epicevents/main.py check-token
```

Use this command to check the status of the current JWT token. You will be prompted to enter a username. The command will inform you whether your session is active or if the token has expired and needs to be refreshed.

- **Logout:**

```sh
python epicevents/main.py logout
```

This command logs out the current user by deleting the stored JWT token and associated data. This will effectively end the user's session.

## User Menu

Upon successful login, users are presented with a menu tailored to their department. Below is a detailed description of the menu options available for each department, the information required, and the actions performed by each option.

**General Menu Options**

These options are available in all department menus:

- **List All**
    - **List Clients:** Displays a list of all clients.
    - **List Contracts:** Displays a list of all contracts.
    - **List Events:** Displays a list of all events.
    - **Return to Main Menu:** Returns to the main menu.

- **Logout**
        Logs out the current user and deletes the stored JWT token.

- **Quit**
        Exits the application.

**Gestion Department Menu**

- **Manage Collaborators**
    - **Create Collaborator:** Prompts the user to enter collaborator details such as username, password, email, name, and department. Creates a new collaborator.
    - **Update Collaborator:** Prompts the user to enter the collaborator ID and new details to update an existing collaborator.
    - **Delete Collaborator:** Prompts the user to enter the collaborator ID to delete an existing collaborator.
    - **Return to Main Menu:** Returns to the main menu.

- **Manage Contracts**
    - **Create Contract:** Prompts the user to enter contract details such as client name, total amount, amount due, and signed status. Creates a new contract.
    - **Update Contract:** Prompts the user to enter the contract ID and new details to update an existing contract.
    - **Return to Main Menu:** Returns to the main menu.

- **Manage Events**
    - **Update Event Support Contact:** Prompts the user to enter the event ID and new support contact details to update the support contact for an existing event.
    - **Filter Events:** Allows the user to filter events based on criteria such as events with no support contact, by client, date range, location, or attendance.
    - **Return to Main Menu:** Returns to the main menu.


**Commercial Department Menu**

- **Manage Clients**
    - **Create Client:** Prompts the user to enter client details such as full name, email, phone, and company name. Creates a new client in the system.
    - **Update Client:** Prompts the user to enter the client ID and new details to update an existing client. Only the commercial contact associated with the client can perform this action.
    - **Return to Main Menu:** Returns to the main menu.

- **Manage Contracts**
    - **Update Contract:** Prompts the user to enter the contract ID and new details to update an existing contract. The user can update contracts for the clients they are responsible for.
    - **Filter Contracts:** Allows the user to filter contracts based on criteria such as unsigned or unpaid contracts.
    - **Return to Main Menu:** Returns to the main menu.

- **Manage Events**
    - **Create Event:** Prompts the user to enter event details such as contract ID, event name, start and end date, location, attendees, and notes. Creates an event for one of their clients who has signed a contract, if the user is authorized.
    - **Return to Main Menu:** Returns to the main menu.

**Support Department Menu**

- **Manage Events**
    - **Filter Events:** Allows the user to filter events based on criteria such as events assigned to the user, by client, date range, location, or attendance.
    - **Update Event:** Prompts the user to enter the event ID and new details to update an existing event. Only the support contact associated with the event can perform this action.
    - **Return to Main Menu:** Returns to the main menu.