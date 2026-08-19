import pytest


pytestmark = pytest.mark.dynamic

EXPECTED_CORE_ENDPOINTS = { 
    #Checks all the core endpoints, also catches in case somebody deletes "POST /upload"
    ("GET", "/"),
    ("GET", "/health"),
    ("POST", "/auth/register"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),
    ("GET", "/auth/me"),
    ("POST", "/upload"),
    ("GET", "/jobs"),
}

HTTP_METHODS = {
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "options",
    "head",
}

def _get_openapi(live_session, base_url):   #Gets API specification as a Python dictionary
    response = live_session.get(f"{base_url}/openapi.json", timeout=5)

    assert response.status_code == 200, response.text

    payload = response.json()

    assert isinstance(payload.get("paths"), dict), ("OpenAPI document does not contain a valid 'paths' object")

    return payload

def test_openapi_document_is_available(live_session, base_url): #Verified that the API can generate its OpenAPI definition
    payload = _get_openapi(live_session, base_url)

    assert payload.get("openapi")
    assert payload.get("info", {}).get("title")

def test_core_orion_api_is_present_in_openapi(live_session, base_url):  #Dynamically discover routes and checks missing endpoints compared to the expected contract
    payload = _get_openapi(live_session, base_url)

    discovered = {
        (method.upper(), path)
        for path, item in payload["paths"].items()
        for method in item
        if method.lower() in HTTP_METHODS
    }

    missing = EXPECTED_CORE_ENDPOINTS - discovered

    assert not missing, (f"Missing documented core endpoints: {sorted(missing)}")

def test_every_discovered_operation_has_responses(live_session, base_url):
    payload = _get_openapi(live_session, base_url)

    for path, item in payload["paths"].items():
        for method, operation in item.items():
            if method.lower() not in HTTP_METHODS:
                continue

            assert isinstance(operation, dict), (
                f"{method.upper()} {path} has an invalid operation definition"
            )

            assert operation.get("responses"), (
                f"{method.upper()} {path} has no documented responses"
            )

@pytest.mark.parametrize("path", ["/", "/health"])  #Verifies that the actual backend is alive
def test_public_smoke_endpoints_are_reachable(live_session, base_url, path):
    response = live_session.get(f"{base_url}{path}", timeout=5)
    assert response.status_code == 200

def test_openapi_security_matches_protected_route_design(live_session, base_url):
    #Verify that OpenAPI security matches the expected public/protected route design

    payload = _get_openapi(live_session, base_url)

    paths = payload["paths"]
    global_security = payload.get("security")

    public_routes = {
        ("GET", "/"),
        ("GET", "/health"),
    }

    protected_routes = {
        ("GET", "/auth/me"),
        ("GET", "/jobs"),
        ("POST", "/upload"),
    }

    # Public routes must explicitly override any global
    # authentication requirement.
    for method, path in public_routes:
        assert path in paths, f"Expected route {method} {path} not found"

        operation = paths[path].get(method.lower())

        assert operation is not None, (
            f"Expected operation {method} {path} not found"
        )

        assert operation.get("security") == [], (
            f"Public endpoint {method} {path} does not explicitly "
            "disable authentication"
        )

    # Protected routes can either define security themselves
    # or inherit it from the global OpenAPI security definition.
    for method, path in protected_routes:
        assert path in paths, f"Expected route {method} {path} not found"

        operation = paths[path].get(method.lower())

        assert operation is not None, (
            f"Expected operation {method} {path} not found"
        )

        operation_security = operation.get("security")

        assert operation_security or global_security, (
            f"Protected endpoint {method} {path} does not "
            "advertise or inherit a security requirement"
        )
