import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from config import Config
from utils.database_initializer import DatabaseInitializer

@pytest.fixture(scope='session')
def setup_database():
    """Fixture to initialize the database using DatabaseInitializer."""
    db_initializer = DatabaseInitializer(test=True)
    db_initializer.initialize()

@pytest.fixture(scope='session')
def engine(setup_database):
    """Fixture to create the database engine."""
    db_uri = Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD, test=True)
    engine = create_engine(db_uri)
    return engine

@pytest.fixture(scope='function')
def db_session(engine, request):
    """Fixture to create a new database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    # Print table contents before rolling back the transaction if the option is enabled
    if request.config.getoption("--print-table-contents"):
        meta = MetaData()
        meta.reflect(bind=engine)
        for table in reversed(meta.sorted_tables):
            result = connection.execute(table.select()).fetchall()
            print(f"Contents of {table.name}: {result}")

    session.rollback()  # Rollback the session to undo any changes made during the test
    session.close()
    transaction.rollback()  # Rollback the transaction to revert the database state
    connection.close()

def pytest_addoption(parser):
    parser.addoption(
        "--print-table-contents", action="store_true", default=False, help="Print table contents before rolling back the transaction"
    )
