# EpicEvents

This project involves setting up a MySQL database for a CRM application using SQLAlchemy in Python. The project includes scripts for creating the database and importing the necessary schema.

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

Create a .env file in the root directory of the project and add the following configuration:

```code
DB_NAME=epicevents
DB_USER=username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

ADMIN_DB_USER=root
ADMIN_DB_PASSWORD=root_password
SENTRY_DSN=your_dsn
```

Ensure that the ADMIN_DB_USER and ADMIN_DB_PASSWORD match your MySQL root user credentials.

4. **Prepare the Database**

Before running the script, make sure your MySQL server is running.

```sh
sudo systemctl start mysql  # On Linux systems
```

Then, run the `epicevents/main.py` script to set up the database and import the schema.

```sh
python epicevents/main.py
```