from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel


class WorkflowRun(SQLModel, table=True):
    """Processing record for one lab message (``workflow_runs`` table)."""

    __tablename__ = "workflow_runs"

    workflow_run_id: str = Field(primary_key=True)
    message_id: str = Field(
        foreign_key="lab_messages.message_id",
        unique=True,
        nullable=False,
    )
    state: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    events: list["WorkflowEvent"] = Relationship(back_populates="workflow_run")


class WorkflowEvent(SQLModel, table=True):
    """Append-only audit row for a workflow transition (``workflow_events`` table)."""

    __tablename__ = "workflow_events"

    event_id: int | None = Field(default=None, primary_key=True)
    workflow_run_id: str = Field(
        foreign_key="workflow_runs.workflow_run_id",
        nullable=False,
    )
    event_type: str
    phase: str
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    workflow_run: WorkflowRun | None = Relationship(back_populates="events")
