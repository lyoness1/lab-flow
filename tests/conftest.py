import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, SQLModel

# Register SQLModel table metadata before create_all.
import labflow.database.lab_message  # noqa: F401
import labflow.database.workflow  # noqa: F401
from labflow.app import create_app
from labflow.database import configure_database, get_engine

_TRUNCATE_SQL = text(
    "TRUNCATE TABLE workflow_events, workflow_runs, lab_messages "
    "RESTART IDENTITY CASCADE"
)


def _truncate_lab_tables() -> None:
    """Remove all rows from application tables.

    Pytest does not reset external databases between tests. HTTP integration
    tests commit through the app, so we truncate explicitly for isolation.
    """
    with Session(get_engine()) as session:
        session.exec(_TRUNCATE_SQL)
        session.commit()


@pytest.fixture(scope="session")
def database_url() -> str:
    """Postgres URL for integration tests (separate from dev ``DATABASE_URL``)."""
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://labflow:labflow@localhost:5432/labflow_test",
    )


@pytest.fixture(scope="session", autouse=True)
def setup_database(database_url: str) -> None:
    configure_database(database_url)
    SQLModel.metadata.create_all(get_engine())


@pytest.fixture
def clean_db() -> None:
    """Empty lab tables before a test (opt-in via pytestmark on DB tests)."""
    _truncate_lab_tables()


@pytest.fixture
def client(database_url: str) -> TestClient:
    app = create_app(database_url=database_url)
    with TestClient(app) as test_client:
        yield test_client
