import json
from pathlib import Path

import pytest

from labflow.constants import API_V0_PREFIX

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "inputs"


def _load_fixture(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text())


def test_create_lab_message_accepts_valid_fixture(client) -> None:
    payload = _load_fixture("lab-message-normal-v0.json")

    response = client.post(f"{API_V0_PREFIX}/lab-messages", json=payload)

    assert response.status_code == 202
    body = response.json()
    assert body["message_id"] == payload["message_id"]
    assert body["state"] == "RECEIVED"
    assert body["workflow_run_id"].startswith("wr_")


def test_create_lab_message_accepts_critical_fixture(client) -> None:
    payload = _load_fixture("lab-message-critical-v0.json")

    response = client.post(f"{API_V0_PREFIX}/lab-messages", json=payload)

    assert response.status_code == 202
    assert response.json()["state"] == "RECEIVED"


@pytest.mark.parametrize(
    "payload",
    [
        {"message_id": "MSG-0001"},
        {
            "schema_version": "lab-message-v0",
            "message_id": "MSG-0001",
            "patient_ref": "pt-8842",
            "observations": [],
        },
        {
            "schema_version": "lab-message-v0",
            "message_id": "MSG-0001",
            "patient_ref": "pt-8842",
            "observations": [{"code": "iron", "value": 1.0, "unit": "g/L"}],
        },
    ],
)
def test_create_lab_message_rejects_invalid_payload(client, payload: dict) -> None:
    response = client.post(f"{API_V0_PREFIX}/lab-messages", json=payload)

    assert response.status_code == 400
