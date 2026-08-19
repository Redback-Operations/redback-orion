import pytest


pytestmark = pytest.mark.dynamic


HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
}


EXPECTED_CORE_ENDPOINTS = {
    ("GET", "/"),
    ("GET", "/health"),

    ("POST", "/auth/register"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),
    ("GET", "/auth/me"),

    ("POST", "/upload"),

    ("GET", "/status/{job_id}"),
    ("GET", "/jobs"),
    ("GET", "/jobs/{job_id}"),
    ("POST", "/jobs/{job_id}/retry"),
    ("DELETE", "/jobs/{job_id}"),
    ("GET", "/jobs/{job_id}/heatmap"),

    ("POST", "/api/players"),
    ("POST", "/api/crowd"),
    ("GET", "/api/test"),
}


PUBLIC_ENDPOINTS = {
    ("GET", "/"),
    ("GET", "/health"),
    ("GET", "/api/test"),
    ("POST", "/api/players"),
    ("POST", "/api/crowd"),
    ("POST", "/auth/register"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),
}


PROTECTED_ENDPOINTS = {
    ("GET", "/auth/me"),
    ("POST", "/upload"),
    ("GET", "/status/{job_id}"),
    ("GET", "/jobs"),
    ("GET", "/jobs/{job_id}"),
    ("POST", "/jobs/{job_id}/retry"),
    ("DELETE", "/jobs/{job_id}"),
    ("GET", "/jobs/{job_id}/heatmap"),
}


def discovered_operations(openapi):
    """
    Convert the OpenAPI paths object into a set of:

        (HTTP_METHOD, PATH)

    tuples.
    """
    discovered = set()

    for path, path_item in openapi["paths"].items():
        for method in path_item:
            method_upper = method.upper()

            if method_upper in HTTP_METHODS:
                discovered.add((method_upper, path))

    return discovered


def get_operation(openapi, method, path):
    """Return one OpenAPI operation."""
    assert path in openapi["paths"], (
        f"OpenAPI path missing: {path}"
    )

    operation = openapi["paths"][path].get(method.lower())

    assert operation is not None, (
        f"OpenAPI operation missing: {method} {path}"
    )

    return operation


def test_openapi_document_is_available(openapi):
    """The running backend must expose a valid OpenAPI document."""
    assert openapi.get("openapi")
    assert openapi.get("info")

    assert openapi["info"].get("title"), (
        "OpenAPI info.title is missing"
    )

    assert openapi["info"].get("version"), (
        "OpenAPI info.version is missing"
    )


def test_expected_core_endpoints_exist(openapi):
    """
    Detect accidental deletion or renaming of important backend routes.
    """
    discovered = discovered_operations(openapi)

    missing = EXPECTED_CORE_ENDPOINTS - discovered

    assert not missing, (
        "Core Orion API endpoints are missing from OpenAPI: "
        f"{sorted(missing)}"
    )


def test_no_duplicate_operation_ids(openapi):
    """
    FastAPI operation IDs should be unique.

    Duplicate operation IDs make generated API clients unreliable.
    """
    operation_ids = {}

    for path, path_item in openapi["paths"].items():
        for method, operation in path_item.items():
            if method.upper() not in HTTP_METHODS:
                continue

            operation_id = operation.get("operationId")

            if not operation_id:
                continue

            operation_ids.setdefault(operation_id, []).append(
                f"{method.upper()} {path}"
            )

    duplicates = {
        operation_id: routes
        for operation_id, routes in operation_ids.items()
        if len(routes) > 1
    }

    assert not duplicates, (
        f"Duplicate OpenAPI operation IDs detected: {duplicates}"
    )


def test_every_operation_documents_responses(openapi):
    """
    Every discovered API operation must describe at least one response.
    """
    for path, path_item in openapi["paths"].items():
        for method, operation in path_item.items():
            if method.upper() not in HTTP_METHODS:
                continue

            assert isinstance(operation, dict), (
                f"{method.upper()} {path} has an invalid operation"
            )

            responses = operation.get("responses")

            assert isinstance(responses, dict), (
                f"{method.upper()} {path} has no response definition"
            )

            assert responses, (
                f"{method.upper()} {path} has an empty response definition"
            )


def test_path_parameters_are_declared(openapi):
    """
    Every {parameter} appearing in a URL path should have a corresponding
    OpenAPI path parameter.
    """
    for path, path_item in openapi["paths"].items():
        path_parameters = {
            segment[1:-1]
            for segment in path.split("/")
            if segment.startswith("{") and segment.endswith("}")
        }

        if not path_parameters:
            continue

        declared = set()

        parameters = path_item.get("parameters", [])

        for parameter in parameters:
            if parameter.get("in") == "path":
                declared.add(parameter.get("name"))

        for method, operation in path_item.items():
            if method.upper() not in HTTP_METHODS:
                continue

            for parameter in operation.get("parameters", []):
                if parameter.get("in") == "path":
                    declared.add(parameter.get("name"))

        missing = path_parameters - declared

        assert not missing, (
            f"{method.upper()} {path} uses undeclared path parameters: "
            f"{sorted(missing)}"
        )


def test_public_routes_do_not_advertise_authentication(openapi):
    """
    Public routes should not accidentally become protected.
    """
    for method, path in PUBLIC_ENDPOINTS:
        operation = get_operation(openapi, method, path)

        security = operation.get("security")

        assert security == [], (
            f"Public endpoint {method} {path} does not explicitly "
            "disable authentication in OpenAPI"
        )


def test_protected_routes_advertise_authentication(openapi):
    """
    Protected routes must advertise an authentication requirement.
    """
    global_security = openapi.get("security")

    for method, path in PROTECTED_ENDPOINTS:
        operation = get_operation(openapi, method, path)

        operation_security = operation.get("security")

        assert operation_security or global_security, (
            f"Protected endpoint {method} {path} does not advertise "
            "an OpenAPI security requirement"
        )


def test_authentication_scheme_exists(openapi):
    """
    The OpenAPI document should define the bearer authentication scheme
    used by the backend.
    """
    schemes = (
        openapi
        .get("components", {})
        .get("securitySchemes", {})
    )

    assert schemes, "No OpenAPI security schemes were defined"

    bearer_schemes = [
        name
        for name, scheme in schemes.items()
        if scheme.get("type") == "http"
        and scheme.get("scheme", "").lower() == "bearer"
    ]

    assert bearer_schemes, (
        "No HTTP Bearer security scheme was found in OpenAPI"
    )


@pytest.mark.parametrize(
    "path",
    ["/", "/health"],
)
def test_public_smoke_endpoints_are_reachable(
    live_session,
    base_url,
    path,
):
    """Basic live smoke test for public gateway endpoints."""
    response = live_session.get(
        f"{base_url}{path}",
        timeout=5,
    )

    assert response.status_code == 200, response.text
    assert response.headers.get("content-type", "").startswith(
        "application/json"
    )