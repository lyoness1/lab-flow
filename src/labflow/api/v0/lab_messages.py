from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, select

from labflow.api.v0.errors import ApiErrorResponse
from labflow.constants import WORKFLOW_RUN_ID_PREFIX
from labflow.database import get_db
from labflow.database.lab_message import LabMessage
from labflow.database.workflow import WorkflowEvent, WorkflowRun
from labflow.utils import compute_payload_hash, create_id

router = APIRouter()


class Observation(BaseModel):
    """One analyte measurement in a ``POST /lab-messages`` body."""

    model_config = ConfigDict(extra="forbid")

    code: Literal["potassium", "sodium", "glucose"]
    value: float
    unit: str = Field(min_length=1)


class LabMessagesBody(BaseModel):
    """Request body for ``POST /lab-messages``."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["lab-message-v0"]
    message_id: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    observations: list[Observation] = Field(min_length=1)


class LabMessagesResponse(BaseModel):
    """Response body for ``POST /lab-messages``."""

    model_config = ConfigDict(extra="forbid")

    workflow_run_id: str = Field(pattern=r"^wr_[0-9a-f]{12}$")
    message_id: str
    state: Literal["RECEIVED"] = "RECEIVED"


@router.post("/lab-messages")
def create_lab_message(
    body: LabMessagesBody,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Accept a lab message: persist, deduplicate, and start a workflow run.

    Returns:
        202 — new message accepted and persisted.
        200 — same ``message_id`` and body as an earlier request (safe retry).
        409 — same ``message_id`` but a different body (sender must use a new ID).
        400 — invalid payload (handled by the global validation error handler).
    """
    raw_payload = body.model_dump(mode="json")
    payload_hash = compute_payload_hash(raw_payload)

    existing = db.get(LabMessage, body.message_id)
    if existing is not None:
        if existing.payload_hash != payload_hash:
            conflict = ApiErrorResponse.from_conflict()
            return JSONResponse(
                status_code=conflict.status,
                content=conflict.model_dump(mode="json"),
            )
        # Idempotent retry: return the workflow run created on the first request.
        run = db.exec(
            select(WorkflowRun).where(WorkflowRun.message_id == body.message_id)
        ).one()
        response = LabMessagesResponse(
            workflow_run_id=run.workflow_run_id,
            message_id=body.message_id,
        )
        return JSONResponse(
            status_code=200,
            content=response.model_dump(mode="json"),
        )

    workflow_run_id = create_id(WORKFLOW_RUN_ID_PREFIX)

    db.add(
        LabMessage(
            message_id=body.message_id,
            patient_ref=body.patient_ref,
            schema_version=body.schema_version,
            raw_payload=raw_payload,
            payload_hash=payload_hash,
        )
    )
    db.add(
        WorkflowRun(
            workflow_run_id=workflow_run_id,
            message_id=body.message_id,
            state="RECEIVED",
        )
    )
    db.add(
        WorkflowEvent(
            workflow_run_id=workflow_run_id,
            event_type="workflow.created",
            phase="validate",
            payload={},
        )
    )
    db.commit()

    response = LabMessagesResponse(
        workflow_run_id=workflow_run_id,
        message_id=body.message_id,
    )
    return JSONResponse(
        status_code=202,
        content=response.model_dump(mode="json"),
    )
