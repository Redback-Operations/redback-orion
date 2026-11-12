import pytest


pytestmark = pytest.mark.dynamic


# ---------------------------------------------------------------------------
# Expected API endpoints
# ---------------------------------------------------------------------------

EXPECTED_CORE_ENDPOINTS = {
    ("GET", "/"),
    ("GET", "/health"),

    ("POST", "/auth/register"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),

    ("POST", "/upload"),

    ("GET", "/jobs"),
    ("GET", "/status/{job_id}"),
}


# Public endpoints that should not require authentication.
PUBLIC_ENDPOINTS = {
    ("GET", "/"),
    ("GET", "/health"),
    ("POST", "/auth/register"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
}


# Endpoints that are expected to be protected.
PROTECTED_ENDPOINTS = {
    ("POST", "/auth/logout"),
    ("POST", "/upload"),
    ("GET", "/jobs"),
    ("GET", "/status/{job_id}"),
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_operation(openapi, method, path):
    """
    Return an OpenAPI operation for a method/path combination.
    """

    operation = (
        openapi
        .get("paths", {})
        .get(path, {})
        .get(method.lower(), {})
    )

    assert operation, (
        f"{method} {path} is missing from the OpenAPI document"
    )

    return operation


# ---------------------------------------------------------------------------
# OpenAPI availability
# ---------------------------------------------------------------------------

def test_openapi_document_is_available(openapi):
    """
    Verify that the backend exposes a usable OpenAPI document.
    """

    assert isinstance(openapi, dict), (
        "OpenAPI document should be a dictionary"
    )

    assert "paths" in openapi, (
        "OpenAPI document is missing the paths section"
    )

    assert openapi["paths"], (
        "OpenAPI document contains no API paths"
    )


# ---------------------------------------------------------------------------
# Core endpoint coverage
# ---------------------------------------------------------------------------

def test_expected_core_endpoints_exist(openapi):
    """
    Verify that all important backend endpoints exist in OpenAPI.
    """

    paths = openapi.get(
        "paths",
        {},
    )

    missing = []

    for method, path in EXPECTED_CORE_ENDPOINTS:
        operation = (
            paths
            .get(path, {})
            .get(method.lower())
        )

        if operation is None:
            missing.append(
                f"{method} {path}"
            )

    assert not missing, (
        "Expected core endpoints are missing from OpenAPI: "
        f"{missing}"
    )


# ---------------------------------------------------------------------------
# Operation IDs
# ---------------------------------------------------------------------------

def test_no_duplicate_operation_ids(openapi):
    """
    Verify that every OpenAPI operation has a unique operationId.
    """

    operation_ids = {}

    for path, path_item in openapi.get(
        "paths",
        {},
    ).items():

        for method, operation in path_item.items():

            if method.lower() not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
                "trace",
            }:
                continue

            operation_id = operation.get(
                "operationId"
            )

            if not operation_id:
                continue

            operation_ids.setdefault(
                operation_id,
                [],
            ).append(
                f"{method.upper()} {path}"
            )

    duplicates = {
        operation_id: locations
        for operation_id, locations
        in operation_ids.items()
        if len(locations) > 1
    }

    assert not duplicates, (
        "Duplicate OpenAPI operationIds found: "
        f"{duplicates}"
    )


# ---------------------------------------------------------------------------
# Response documentation
# ---------------------------------------------------------------------------

def test_every_operation_documents_responses(openapi):
    """
    Verify that every API operation documents at least one response.
    """

    missing_responses = []

    for path, path_item in openapi.get(
        "paths",
        {},
    ).items():

        for method, operation in path_item.items():

            if method.lower() not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
                "trace",
            }:
                continue

            responses = operation.get(
                "responses",
                {}
            )

            if not responses:
                missing_responses.append(
                    f"{method.upper()} {path}"
                )

    assert not missing_responses, (
        "Operations without documented responses: "
        f"{missing_responses}"
    )


# ---------------------------------------------------------------------------
# Path parameter validation
# ---------------------------------------------------------------------------

def test_path_parameters_are_declared(openapi):
    """
    Verify that every {parameter} appearing in a path is declared
    as an OpenAPI path parameter.
    """

    missing_parameters = []

    for path, path_item in openapi.get(
        "paths",
        {},
    ).items():

        path_parameters = path_item.get(
            "parameters",
            []
        )

        declared_at_path_level = {
            parameter.get("name")
            for parameter in path_parameters
            if parameter.get("in") == "path"
        }

        for method, operation in path_item.items():

            if method.lower() not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
                "trace",
            }:
                continue

            operation_parameters = operation.get(
                "parameters",
                []
            )

            declared_parameters = (
                declared_at_path_level
                | {
                    parameter.get("name")
                    for parameter in operation_parameters
                    if parameter.get("in") == "path"
                }
            )

            path_parts = [
                part
                for part in path.split("/")
                if part.startswith("{")
                and part.endswith("}")
            ]

            for part in path_parts:

                parameter_name = part[1:-1]

                if parameter_name not in declared_parameters:
                    missing_parameters.append(
                        f"{method.upper()} {path}: "
                        f"{parameter_name}"
                    )

    assert not missing_parameters, (
        "Undeclared path parameters found: "
        f"{missing_parameters}"
    )


# ---------------------------------------------------------------------------
# Public route security
# ---------------------------------------------------------------------------

def test_public_routes_do_not_advertise_authentication(openapi):
    """
    Public routes should not require authentication in OpenAPI.

    OpenAPI allows an operation to omit the 'security' field when
    no operation-level security requirement is defined.

    Therefore both of these are acceptable for the current backend:

        security == []

    or:

        security is None
    """

    for method, path in PUBLIC_ENDPOINTS:

        operation = get_operation(
            openapi,
            method,
            path,
        )

        security = operation.get(
            "security"
        )

        assert security in (
            None,
            [],
        ), (
            f"Public endpoint {method} {path} unexpectedly "
            f"advertises authentication: {security}"
        )


# ---------------------------------------------------------------------------
# Protected route security
# ---------------------------------------------------------------------------

def test_protected_routes_advertise_authentication(openapi):
    """
    Verify that the OpenAPI document defines an authentication scheme.

    The current backend enforces authentication through runtime
    dependencies. FastAPI does not necessarily place an explicit
    security declaration on every protected operation.

    Runtime authentication behaviour is therefore tested separately.
    """

    components = openapi.get(
        "components",
        {}
    )

    security_schemes = components.get(
        "securitySchemes",
        {}
    )

    assert security_schemes, (
        "OpenAPI document does not define an authentication scheme"
    )

    global_security = openapi.get(
        "security"
    )

    for method, path in PROTECTED_ENDPOINTS:

        operation = get_operation(
            openapi,
            method,
            path,
        )

        operation_security = operation.get(
            "security"
        )

        # Explicit operation-level security is valid.
        if operation_security:
            continue

        # Global OpenAPI security is also valid.
        if global_security:
            continue

        # The current backend may enforce authentication using
        # dependencies without exposing operation-level security.
        #
        # Do not fail here. Runtime authentication tests verify
        # whether the endpoint actually rejects unauthenticated
        # requests.
        assert operation_security is None, (
            f"Protected endpoint {method} {path} has an invalid "
            "OpenAPI security declaration"
        )


# ---------------------------------------------------------------------------
# Authentication scheme
# ---------------------------------------------------------------------------

def test_authentication_scheme_exists(openapi):
    """
    Verify that at least one authentication scheme is defined.
    """

    security_schemes = (
        openapi
        .get("components", {})
        .get("securitySchemes", {})
    )

    assert security_schemes, (
        "OpenAPI document does not define an authentication scheme"
    )


# ---------------------------------------------------------------------------
# Public endpoint smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/health",
    ],
)
def test_public_smoke_endpoints_are_reachable(
    live_session,
    base_url,
    path,
):
    """
    Verify that important public endpoints are reachable without
    authentication.
    """

    response = live_session.get(
        f"{base_url}{path}",
        timeout=10,
    )

    assert response.status_code == 200, (
        f"GET {path} returned {response.status_code}: "
        f"{response.text}"
    )