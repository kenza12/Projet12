from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import Config


def create_engines():
    """
    Creates and returns SQLAlchemy engines for user, admin, and test databases.

    Returns:
        tuple: (engine_user, engine_admin, engine_test)
    """
    engine_user = create_engine(Config.get_db_uri(Config.DB_USER, Config.DB_PASSWORD))
    engine_admin = create_engine(Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD))
    engine_test = create_engine(Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD, test=True))
    return engine_user, engine_admin, engine_test


# Create global engines
engine_user, engine_admin, engine_test = create_engines()

# Create configured "Session" classes
SessionUser = sessionmaker(bind=engine_user)
SessionAdmin = sessionmaker(bind=engine_admin)
SessionTest = sessionmaker(bind=engine_test)


def get_session():
    """
    Creates and returns a new SQLAlchemy session for non-privileged user.

    Returns:
        Session: SQLAlchemy session object.
    """
    if Config.get_use_test_database():
        return SessionTest()
    return SessionUser()


def get_session_root():
    """
    Creates and returns a new SQLAlchemy session for admin user.

    Returns:
        Session: SQLAlchemy session object.
    """
    if Config.get_use_test_database():
        return SessionTest()
    return SessionAdmin()
