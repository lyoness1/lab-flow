import json
from pathlib import Path

import pytest

from labflow.constants import API_V0_PREFIX, WORKFLOW_RUN_ID_PREFIX

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "inputs"


def _load_fixture(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text())


def _post_lab_message(client, payload: dict):
    return client.post(f"{API_V0_PREFIX}/lab-messages", json=payload)


def _assert_validation_error(response, *, field: str) -> None:
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == 400
    assert body["code"] == "validation_error"
    assert body["message"] == "Request validation failed"
    assert isinstance(body["details"], list)
    assert body["details"]
    fields = {item["field"] for item in body["details"]}
    assert field in fields
    for item in body["details"]:
        assert set(item) == {"field", "message"}
        assert isinstance(item["message"], str) and item["message"]


def test_create_lab_message_accepts_valid_fixture(client) -> None:
    payload = _load_fixture("lab-message-normal-v0.json")

    response = _post_lab_message(client, payload)

    assert response.status_code == 202
    body = response.json()
    assert body["message_id"] == payload["message_id"]
    assert body["state"] == "RECEIVED"
    assert body["workflow_run_id"].startswith(WORKFLOW_RUN_ID_PREFIX)


def test_create_lab_message_accepts_critical_fixture(client) -> None:
    payload = _load_fixture("lab-message-critical-v0.json")

    response = _post_lab_message(client, payload)

    assert response.status_code == 202
    assert response.json()["state"] == "RECEIVED"


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
def test_create_lab_message_rejects_invalid_payload(
    client,
    payload: dict,
    expected_field: str,
) -> None:
    response = _post_lab_message(client, payload)
    _assert_validation_error(response, field=expected_field)
