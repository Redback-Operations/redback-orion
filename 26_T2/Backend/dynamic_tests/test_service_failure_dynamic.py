import threading
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import pytest

from app.routes import health


pytestmark = pytest.mark.dynamic


class FailureHandler(BaseHTTPRequestHandler):
    """
    Tiny local HTTP service used to simulate a failed downstream service.
    """

    def do_GET(self):
        self.send_response(503)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.end_headers()

        self.wfile.write(
            b'{"status":"service unavailable"}'
        )

    def log_message(self, format, *args):
        return


@pytest.fixture
def failing_service():
    """
    Start a temporary local service that always returns HTTP 503.
    """
    server = HTTPServer(
        ("127.0.0.1", 0),
        FailureHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.asyncio
async def test_health_reports_failed_downstream_service(
    monkeypatch,
    failing_service,
):
    """
    A reachable downstream service returning HTTP 503 should be reported
    as 'error' by the gateway health endpoint.
    """

    monkeypatch.setattr(
        health,
        "PLAYER_SERVICE_URL",
        failing_service,
    )

    # Use a deliberately unused local port for the second service.
    monkeypatch.setattr(
        health,
        "CROWD_SERVICE_URL",
        "http://127.0.0.1:1",
    )

    result = await health.health_check()

    assert result["gateway"] == "ok"

    assert result["player_service"] == "error"

    assert result["crowd_service"] == "unreachable"


@pytest.mark.asyncio
async def test_health_reports_unreachable_services(
    monkeypatch,
):
    """
    If both downstream services cannot be reached, the gateway itself
    should remain available and report them as unreachable.
    """

    monkeypatch.setattr(
        health,
        "PLAYER_SERVICE_URL",
        "http://127.0.0.1:1",
    )

    monkeypatch.setattr(
        health,
        "CROWD_SERVICE_URL",
        "http://127.0.0.1:2",
    )

    result = await health.health_check()

    assert result["gateway"] == "ok"

    assert result["player_service"] == "unreachable"

    assert result["crowd_service"] == "unreachable"


@pytest.mark.asyncio
async def test_health_detects_one_failed_service_and_one_unreachable_service(
    monkeypatch,
    failing_service,
):
    """
    The gateway must report each downstream service independently.
    """

    monkeypatch.setattr(
        health,
        "PLAYER_SERVICE_URL",
        failing_service,
    )

    monkeypatch.setattr(
        health,
        "CROWD_SERVICE_URL",
        "http://127.0.0.1:2",
    )

    result = await health.health_check()

    assert result["gateway"] == "ok"
    assert result["player_service"] == "error"
    assert result["crowd_service"] == "unreachable"


def test_live_health_endpoint_exposes_downstream_status(
    live_session,
    base_url,
):
    """
    Confirm the live gateway exposes independent downstream health fields.
    """
    response = live_session.get(
        f"{base_url}/health",
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["gateway"] == "ok"

    assert data["player_service"] in {
        "ok",
        "error",
        "unreachable",
        "pending",
    }

    assert data["crowd_service"] in {
        "ok",
        "error",
        "unreachable",
        "pending",
    }