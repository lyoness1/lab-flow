import os

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

import labflow.database.lab_message  # noqa: F401 — register table metadata
import labflow.database.workflow  # noqa: F401

_engine: Engine | None = None


def configure_database(database_url: str | None = None) -> None:
    """Create the engine and ensure all SQLModel tables exist."""
    global _engine

    url = database_url or os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://labflow:labflow@localhost:5432/labflow",
    )
    _engine = create_engine(url, echo=False)
    SQLModel.metadata.create_all(_engine)


def get_engine() -> Engine:
    """Return the configured engine, initializing with defaults if needed."""
    if _engine is None:
        configure_database()
    assert _engine is not None
    return _engine


def get_session() -> Session:
    """Open a new SQLModel session (caller must close)."""
    return Session(get_engine())


def get_db():
    """FastAPI dependency that yields a session and closes it after the request."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()
