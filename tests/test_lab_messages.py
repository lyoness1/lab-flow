from collections.abc import Callable

import pytest
from sqlmodel import func, select

from factories.lab_message import lab_message_critical, lab_message_normal
from labflow.api.v0.lab_messages import LabMessagesBody
from labflow.constants import API_V0_PREFIX, WORKFLOW_RUN_ID_PREFIX
from labflow.database import get_session
from labflow.database.lab_message import LabMessage
from labflow.database.workflow import WorkflowEvent, WorkflowRun

pytestmark = pytest.mark.usefixtures("clean_db")


def _post_lab_message(client, payload: dict):
    return client.post(f"{API_V0_PREFIX}/lab-messages", json=payload)


@pytest.mark.parametrize(
    "payload_factory",
    [lab_message_normal, lab_message_critical],
    ids=["normal", "critical"],
)
def test_create_lab_message_accepts_valid_payload_and_deduplicates_on_retry(
    client,
    payload_factory: Callable[[], LabMessagesBody],
) -> None:
    """Happy path: empty DB → 202 + persist → 200 retry without duplicating rows."""
    payload = payload_factory().model_dump(mode="json")

    # clean_db ran, but confirm we start from an empty database
    session = get_session()
    try:
        assert session.exec(select(func.count()).select_from(LabMessage)).one() == 0
        assert session.exec(select(func.count()).select_from(WorkflowRun)).one() == 0
        assert session.exec(select(func.count()).select_from(WorkflowEvent)).one() == 0
    finally:
        session.close()

    # first delivery: new message_id → 202 Accepted
    first = _post_lab_message(client, payload)
    assert first.status_code == 202
    first_body = first.json()
    assert first_body["message_id"] == payload["message_id"]
    assert first_body["state"] == "RECEIVED"
    assert first_body["workflow_run_id"].startswith(WORKFLOW_RUN_ID_PREFIX)

    # one row each; message, workflow run, and workflow.created event persisted
    session = get_session()
    try:
        assert session.exec(select(func.count()).select_from(LabMessage)).one() == 1
        assert session.exec(select(func.count()).select_from(WorkflowRun)).one() == 1
        assert session.exec(select(func.count()).select_from(WorkflowEvent)).one() == 1

        stored = session.get(LabMessage, payload["message_id"])
        assert stored is not None
        assert stored.raw_payload == payload

        run = session.get(WorkflowRun, first_body["workflow_run_id"])
        assert run is not None
        assert run.state == "RECEIVED"
        assert run.message_id == payload["message_id"]

        events = session.exec(
            select(WorkflowEvent).where(
                WorkflowEvent.workflow_run_id == first_body["workflow_run_id"]
            )
        ).all()
        assert len(events) == 1
        assert events[0].event_type == "workflow.created"
        assert events[0].phase == "validate"
        assert events[0].payload == {}
    finally:
        session.close()

    # safe retry: same message_id + same body → 200, same workflow_run_id
    second = _post_lab_message(client, payload)
    assert second.status_code == 200
    assert second.json() == first_body

    # still one row each — retry must not duplicate work
    session = get_session()
    try:
        assert session.exec(select(func.count()).select_from(LabMessage)).one() == 1
        assert session.exec(select(func.count()).select_from(WorkflowRun)).one() == 1
        assert session.exec(select(func.count()).select_from(WorkflowEvent)).one() == 1

        stored = session.get(LabMessage, payload["message_id"])
        assert stored is not None
        assert stored.raw_payload == payload

        run = session.get(WorkflowRun, first_body["workflow_run_id"])
        assert run is not None
        assert run.state == "RECEIVED"
        assert run.message_id == payload["message_id"]

        events = session.exec(
            select(WorkflowEvent).where(
                WorkflowEvent.workflow_run_id == first_body["workflow_run_id"]
            )
        ).all()
        assert len(events) == 1
        assert events[0].event_type == "workflow.created"
        assert events[0].phase == "validate"
        assert events[0].payload == {}
    finally:
        session.close()


def test_create_lab_message_returns_409_for_body_mismatch(client) -> None:
    base = lab_message_normal().model_dump(mode="json")
    _post_lab_message(client, base)

    # same message_id, different body — sender must use a new message_id
    changed = {**base, "patient_ref": "pt-different"}
    response = _post_lab_message(client, changed)

    assert response.status_code == 409
    assert response.json() == {
        "status": 409,
        "code": "conflict",
        "message": "Same message_id with a different request body",
        "details": [],
    }

    # original rows unchanged; conflict must not write a second workflow
    session = get_session()
    try:
        assert session.exec(select(func.count()).select_from(LabMessage)).one() == 1
        assert session.exec(select(func.count()).select_from(WorkflowRun)).one() == 1
        assert session.exec(select(func.count()).select_from(WorkflowEvent)).one() == 1
    finally:
        session.close()


@pytest.mark.parametrize(
    "payload,expected_field",
    [
        pytest.param(
            {"message_id": "MSG-0001"},
            "schema_version",
            id="missing_required_fields",
        ),
        pytest.param(
            {
                "schema_version": "lab-message-v0",
                "message_id": "MSG-0001",
                "patient_ref": "pt-8842",
                "observations": [],
            },
            "observations",
            id="empty_observations_list",
        ),
        pytest.param(
            {
                "schema_version": "lab-message-v0",
                "message_id": "MSG-0001",
                "patient_ref": "pt-8842",
                "observations": [{"code": "iron", "value": 1.0, "unit": "g/L"}],
            },
            "observations.0.code",
            id="invalid_analyte_code",
        ),
    ],
)
def test_create_lab_message_returns_400_for_invalid_payload(
    client,
    payload: dict,
    expected_field: str,
) -> None:
    response = _post_lab_message(client, payload)

    # validation envelope with field-level details
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == 400
    assert body["code"] == "validation_error"
    assert body["message"] == "Request validation failed"
    assert isinstance(body["details"], list)
    assert body["details"]
    fields = {item["field"] for item in body["details"]}
    assert expected_field in fields
    for item in body["details"]:
        assert set(item) == {"field", "message"}
        assert isinstance(item["message"], str) and item["message"]

    # invalid payloads must not touch the database
    session = get_session()
    try:
        assert session.exec(select(func.count()).select_from(LabMessage)).one() == 0
        assert session.exec(select(func.count()).select_from(WorkflowRun)).one() == 0
        assert session.exec(select(func.count()).select_from(WorkflowEvent)).one() == 0
    finally:
        session.close()
