from labflow.constants import API_V0_PREFIX


def test_health_returns_ok(client) -> None:
    response = client.get(f"{API_V0_PREFIX}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
