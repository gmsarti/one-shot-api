from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

# Create declarative base
Base = declarative_base()


def create_database_engine(database_url: str):
    """Create a database engine with the given URL."""
    return create_engine(database_url)


def get_session_maker():
    """Get the session maker."""
    engine = create_database_engine(settings.DATABASE_URL)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get a database session."""
    session_maker = get_session_maker()
    db = None
    try:
        db = session_maker()
        yield db
    except Exception as e:
        raise OperationalError(str(e), None, e)
    finally:
        if db is not None:
            db.close()


def get_db_session_scope():
    """Get a database session scope."""
    session_maker = get_session_maker()
    db = None
    try:
        db = session_maker()
        yield db
    except Exception as e:
        raise OperationalError(str(e), None, e)
    finally:
        if db is not None:
            db.close()
