# EpicEvents

This project involves setting up a MySQL database for a CRM application using SQLAlchemy in Python. The project includes scripts for creating the database, importing the necessary schema, and managing user authentication via JWT tokens

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