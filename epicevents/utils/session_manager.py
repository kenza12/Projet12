from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import Config


# Create global engines
engine_user = create_engine(Config.get_db_uri(Config.DB_USER, Config.DB_PASSWORD))
engine_admin = create_engine(Config.get_db_uri(Config.ADMIN_DB_USER, Config.ADMIN_DB_PASSWORD))

# Create configured "Session" classes
SessionUser = sessionmaker(bind=engine_user)
SessionAdmin = sessionmaker(bind=engine_admin)

def get_session():
    """
    Creates and returns a new SQLAlchemy session for non-privileged user.
    
    Returns:
        Session: SQLAlchemy session object.
    """
    return SessionUser()

def get_session_root():
    """
    Creates and returns a new SQLAlchemy session for admin user.
    
    Returns:
        Session: SQLAlchemy session object.
    """
    return SessionAdmin()