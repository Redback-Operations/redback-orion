def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_gateway_ok(client):
    response = client.get("/health")
    assert response.json()["gateway"] == "ok"


def test_health_has_all_fields(client):
    response = client.get("/health")
    data = response.json()
    assert "gateway" in data
    assert "player_service" in data
    assert "crowd_service" in data
