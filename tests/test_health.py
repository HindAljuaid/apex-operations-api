def test_root_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_root_returns_application_name(client):
    response = client.get("/")
    assert response.json()["application"] == "Apex Operations API"


def test_liveness_returns_200(client):
    response = client.get("/health/live")
    assert response.status_code == 200


def test_liveness_returns_alive_status(client):
    response = client.get("/health/live")
    assert response.json() == {"status": "alive"}


def test_readiness_returns_200(client):
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_readiness_returns_ready_status(client):
    response = client.get("/health/ready")
    assert response.json() == {"status": "ready"}
