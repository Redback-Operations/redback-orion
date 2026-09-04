import socket
import threading
import time
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import pytest
import requests


pytestmark = pytest.mark.dynamic


class FailureHandler(BaseHTTPRequestHandler):
    """
    Temporary local HTTP service that always returns HTTP 503.
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


class SlowHandler(BaseHTTPRequestHandler):
    """
    Temporary local HTTP service that deliberately delays its response.
    This is used to verify timeout handling.
    """

    def do_GET(self):
        time.sleep(10)

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.end_headers()

        self.wfile.write(
            b'{"status":"ok"}'
        )

    def log_message(self, format, *args):
        return


@pytest.fixture
def failing_service():
    """
    Start a temporary local HTTP service that returns HTTP 503.
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


@pytest.fixture
def slow_service():
    """
    Start a temporary local HTTP service that responds slowly.
    """

    server = HTTPServer(
        ("127.0.0.1", 0),
        SlowHandler,
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


def find_unused_local_port():
    """
    Find a local TCP port that is currently unused.
    This is used to simulate a downstream service that cannot be reached.
    """

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as sock:

        sock.bind(("127.0.0.1", 0))

        return sock.getsockname()[1]


def test_failure_service_returns_503(failing_service):
    """
    Verify that the simulated failed downstream service actually returns
    HTTP 503.
    This validates the failure fixture itself before it is used by other
    tests.
    """

    response = requests.get(
        failing_service,
        timeout=5,
    )

    assert response.status_code == 503

    assert response.json()["status"] == "service unavailable"


def test_unreachable_service_cannot_be_connected_to():
    """
    Verify that the test-generated unavailable service is genuinely
    unreachable.
    """

    port = find_unused_local_port()

    with pytest.raises(requests.RequestException):

        requests.get(
            f"http://127.0.0.1:{port}",
            timeout=2,
        )


def test_slow_service_triggers_client_timeout(slow_service):
    """
    Verify that the test environment can detect a downstream timeout.
    This test checks timeout behaviour at the HTTP client level. It does
    not claim that the Orion backend itself has timed out.
    """

    with pytest.raises(requests.Timeout):

        requests.get(
            f"{slow_service}",
            timeout=1,
        )


def test_live_health_endpoint_exposes_downstream_status(
    live_session,
    base_url,
):
    """
    Verify that the live Orion gateway exposes independent health status
    fields for the downstream services.
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