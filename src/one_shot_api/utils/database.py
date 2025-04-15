from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..utils.config import settings

Base = declarative_base()

_engine: Engine | None = None
_SessionLocal = None


def get_database_url() -> str:
    return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


def create_database_engine() -> Engine:
    try:
        return create_engine(get_database_url())
    except Exception as e:
        raise OperationalError("Failed to create database engine", None, e)


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine


def get_session_maker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


# Dependency
def get_db() -> Generator[Session, None, None]:
    try:
        db = get_session_maker()()
        yield db
    except Exception as e:
        raise OperationalError("Failed to create database session", None, e)
    finally:
        if "db" in locals():
            db.close()
