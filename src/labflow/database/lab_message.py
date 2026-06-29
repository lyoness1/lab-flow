from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class LabMessage(SQLModel, table=True):
    """Persisted lab message row in ``lab_messages``.

    Observations live inside ``raw_payload`` (JSONB), not as separate columns.
    """

    __tablename__ = "lab_messages"

    message_id: str = Field(primary_key=True)
    patient_ref: str
    schema_version: str
    raw_payload: dict = Field(sa_column=Column(JSON, nullable=False))
    payload_hash: str
    received_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
