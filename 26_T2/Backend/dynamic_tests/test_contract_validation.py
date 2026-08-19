import pytest


pytestmark = pytest.mark.dynamic

def test_health_response_contract(live_session, base_url):
    response = live_session.get(f"{base_url}/health", timeout=5)

    assert response.status_code == 200

    data = response.json()

    required = {
        "gateway",
        "player_service",
        "crowd_service"
    }

    assert required.issubset(data)

def test_root_response_contract(live_session, base_url):    #Test the content, not just the HTTP status
    response = live_session.get(f"{base_url}/", timeout=5)

    assert response.status_code == 200

    data = response.json()

    assert data.get("status") == "success"
    assert "message" in data

def test_unauthenticated_protected_endpoint_is_rejected(live_session, base_url):    #Security regression test
    response = live_session.get(f"{base_url}/auth/me", timeout=5)

    assert response.status_code == 401
    assert "detail" in response.json()