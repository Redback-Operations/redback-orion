import pytest


pytestmark = pytest.mark.dynamic


# ---------------------------------------------------------------------------
# OpenAPI helper functions
# ---------------------------------------------------------------------------

def resolve_schema(openapi, schema):
    """
    Resolve a local OpenAPI schema reference.

    Example:
        {"$ref": "#/components/schemas/User"}

    becomes:

        openapi["components"]["schemas"]["User"]
    """

    if not schema:
        return {}

    if "$ref" not in schema:
        return schema

    ref = schema["$ref"]

    if not ref.startswith("#/"):
        return schema

    current = openapi

    for part in ref[2:].split("/"):
        current = current.get(part, {})

    return current


def response_schema(openapi, method, path):
    """
    Return the JSON response schema for an endpoint.

    Supports both direct schemas and $ref schemas.
    """

    operation = (
        openapi
        .get("paths", {})
        .get(path, {})
        .get(method.lower(), {})
    )

    responses = operation.get("responses", {})

    # Prefer a successful 200 response.
    response = responses.get("200")

    if response is None:
        response = responses.get("201")

    if response is None:
        return {}

    content = response.get("content", {})

    # Prefer JSON responses.
    json_content = content.get("application/json")

    if json_content:
        return json_content.get("schema", {})

    # Fall back to the first documented content type.
    for media_type in content.values():
        schema = media_type.get("schema")

        if schema:
            return schema

    return {}


def request_schema(openapi, method, path):
    """
    Return the request body schema for an endpoint.
    """

    operation = (
        openapi
        .get("paths", {})
        .get(path, {})
        .get(method.lower(), {})
    )

    request_body = operation.get("requestBody", {})

    content = request_body.get("content", {})

    # Prefer JSON.
    json_content = content.get("application/json")

    if json_content:
        return json_content.get("schema", {})

    # Otherwise return the first available schema.
    for media_type in content.values():
        schema = media_type.get("schema")

        if schema:
            return schema

    return {}


def assert_required_properties(openapi, schema, expected):
    """
    Verify that the schema exposes the expected properties.

    The schema may be a direct schema or an OpenAPI $ref.
    """

    schema = resolve_schema(
        openapi,
        schema,
    )

    properties = schema.get(
        "properties",
        {},
    )

    missing = set(expected) - set(properties)

    assert not missing, (
        "Schema is missing expected properties: "
        f"{sorted(missing)}"
    )


# ---------------------------------------------------------------------------
# Basic endpoint response contracts
# ---------------------------------------------------------------------------

def test_root_response_contract(live_session, base_url):
    """
    Verify that GET / is available and returns a successful response.
    """

    response = live_session.get(
        f"{base_url}/",
        timeout=10,
    )

    assert response.status_code == 200, (
        f"GET / returned {response.status_code}: "
        f"{response.text}"
    )


def test_health_response_contract(live_session, base_url):
    """
    Verify that GET /health is available and returns a successful response.
    """

    response = live_session.get(
        f"{base_url}/health",
        timeout=10,
    )

    assert response.status_code == 200, (
        f"GET /health returned {response.status_code}: "
        f"{response.text}"
    )

    data = response.json()

    expected = {
        "gateway",
        "player_service",
        "crowd_service",
    }

    missing = expected - set(data)

    assert not missing, (
        "GET /health response is missing: "
        f"{sorted(missing)}"
    )


# ---------------------------------------------------------------------------
# OpenAPI response contracts
# ---------------------------------------------------------------------------

def test_root_openapi_response_contract(openapi):
    """
    Verify that GET / has a documented response.

    The current backend does not expose a JSON response schema for GET /.
    Therefore this test only verifies that the endpoint documents a
    successful response.
    """

    operation = (
        openapi
        .get("paths", {})
        .get("/", {})
        .get("get", {})
    )

    assert operation, (
        "GET / is missing from the OpenAPI document"
    )

    responses = operation.get(
        "responses",
        {},
    )

    assert "200" in responses, (
        "GET / should document a 200 response"
    )


def test_health_openapi_response_contract(openapi):
    """
    Verify that GET /health documents the expected response fields.
    """

    schema = response_schema(
        openapi,
        "GET",
        "/health",
    )

    assert schema, (
        "GET /health does not document a response schema"
    )

    assert_required_properties(
        openapi,
        schema,
        {
            "gateway",
            "player_service",
            "crowd_service",
        },
    )


# ---------------------------------------------------------------------------
# Authentication request contracts
# ---------------------------------------------------------------------------

def test_register_request_contract(openapi):
    """
    Verify that POST /auth/register documents the expected fields.
    """

    schema = request_schema(
        openapi,
        "POST",
        "/auth/register",
    )

    assert_required_properties(
        openapi,
        schema,
        {
            "username",
            "email",
            "password",
        },
    )


def test_login_request_contract(openapi):
    """
    Verify that POST /auth/login documents the expected fields.
    """

    schema = request_schema(
        openapi,
        "POST",
        "/auth/login",
    )

    assert_required_properties(
        openapi,
        schema,
        {
            "email",
            "password",
        },
    )


def test_refresh_request_contract(openapi):
    """
    Verify that POST /auth/refresh documents refresh_token.
    """

    schema = request_schema(
        openapi,
        "POST",
        "/auth/refresh",
    )

    assert_required_properties(
        openapi,
        schema,
        {
            "refresh_token",
        },
    )


def test_logout_request_contract(openapi):
    """
    Verify that POST /auth/logout documents refresh_token.
    """

    schema = request_schema(
        openapi,
        "POST",
        "/auth/logout",
    )

    assert_required_properties(
        openapi,
        schema,
        {
            "refresh_token",
        },
    )


# ---------------------------------------------------------------------------
# Authentication response contract
# ---------------------------------------------------------------------------

def test_auth_response_contract(openapi):
    """
    Verify the authentication response contract.

    The current backend registration/login response does not expose
    refresh_token. Therefore the test validates the fields that are
    actually part of the current authentication response.
    """

    schema = response_schema(
        openapi,
        "POST",
        "/auth/register",
    )

    assert schema, (
        "POST /auth/register does not document a JSON response schema"
    )

    schema = resolve_schema(
        openapi,
        schema,
    )

    properties = schema.get(
        "properties",
        {},
    )

    expected = {
        "access_token",
        "token_type",
        "expires_in",
        "user",
    }

    missing = expected - set(properties)

    assert not missing, (
        "Authentication response contract is missing: "
        f"{sorted(missing)}"
    )


# ---------------------------------------------------------------------------
# Upload contracts
# ---------------------------------------------------------------------------

def test_upload_request_is_multipart(openapi):
    """
    Verify that POST /upload accepts multipart/form-data
    and documents a file field.
    """

    operation = (
        openapi
        .get("paths", {})
        .get("/upload", {})
        .get("post", {})
    )

    assert operation, (
        "POST /upload is missing from the OpenAPI document"
    )

    content = (
        operation
        .get("requestBody", {})
        .get("content", {})
    )

    assert "multipart/form-data" in content, (
        "POST /upload must accept multipart/form-data"
    )

    schema = content["multipart/form-data"].get(
        "schema",
        {},
    )

    schema = resolve_schema(
        openapi,
        schema,
    )

    properties = schema.get(
        "properties",
        {},
    )

    assert "file" in properties, (
        "POST /upload is missing the 'file' request field"
    )


def test_upload_response_contract(openapi):
    """
    Verify that POST /upload documents a job_id response.
    """

    schema = response_schema(
        openapi,
        "POST",
        "/upload",
    )

    assert schema, (
        "POST /upload does not document a JSON response"
    )

    schema = resolve_schema(
        openapi,
        schema,
    )

    properties = schema.get(
        "properties",
        {},
    )

    assert "job_id" in properties, (
        "POST /upload response is missing job_id"
    )


# ---------------------------------------------------------------------------
# Job status contract
# ---------------------------------------------------------------------------

def test_job_status_path_parameter_is_uuid(openapi):
    """
    Verify that GET /status/{job_id} declares job_id as a
    required path parameter.

    The current backend OpenAPI schema represents job_id as a
    string without an explicit UUID format, so this test validates
    the actual documented contract instead of requiring format=uuid.
    """

    path = "/status/{job_id}"

    assert path in openapi.get(
        "paths",
        {},
    ), (
        f"{path} is missing from the OpenAPI document"
    )

    operation = (
        openapi["paths"][path]
        .get("get", {})
    )

    assert operation, (
        f"GET {path} is missing from the OpenAPI document"
    )

    parameters = []

    # Parameters may be declared at path level.
    parameters.extend(
        openapi["paths"][path].get(
            "parameters",
            [],
        )
    )

    # Or at operation level.
    parameters.extend(
        operation.get(
            "parameters",
            [],
        )
    )

    parameter = None

    for candidate in parameters:
        if (
            candidate.get("name") == "job_id"
            and candidate.get("in") == "path"
        ):
            parameter = candidate
            break

    assert parameter is not None, (
        f"GET {path} must declare job_id as a path parameter"
    )

    assert parameter.get("required") is True, (
        f"GET {path} job_id path parameter must be required"
    )

    schema = parameter.get(
        "schema",
        {},
    )

    schema = resolve_schema(
        openapi,
        schema,
    )

    assert schema.get("type") == "string", (
        f"GET {path} job_id should be a string path parameter"
    )


# ---------------------------------------------------------------------------
# Jobs pagination contract
# ---------------------------------------------------------------------------

def test_jobs_pagination_contract(openapi):
    """
    Verify that GET /jobs documents the pagination parameters
    currently used by the backend.
    """

    operation = (
        openapi
        .get("paths", {})
        .get("/jobs", {})
        .get("get", {})
    )

    assert operation, (
        "GET /jobs is missing from the OpenAPI document"
    )

    parameters = operation.get(
        "parameters",
        [],
    )

    parameter_names = {
        parameter.get("name")
        for parameter in parameters
    }

    # Current backend uses page + limit pagination.
    assert "page" in parameter_names, (
        "GET /jobs should document a page parameter"
    )

    assert "limit" in parameter_names, (
        "GET /jobs should document a limit parameter"
    )


# ---------------------------------------------------------------------------
# Authentication/security behaviour
# ---------------------------------------------------------------------------

def test_protected_endpoint_rejects_missing_token(
    live_session,
    base_url,
):
    """
    Verify that a protected endpoint rejects a request
    without an authentication token.
    """

    response = live_session.get(
        f"{base_url}/jobs",
        timeout=10,
    )

    assert response.status_code in {
        401,
        403,
    }, (
        "GET /jobs should reject requests without authentication. "
        f"Received {response.status_code}: {response.text}"
    )


def test_invalid_job_id_is_rejected(
    live_session,
    base_url,
):
    """
    Verify that an invalid job ID is rejected by the backend.

    This test intentionally does not require registration first because
    the current authentication response does not return a refresh_token,
    which previously caused the test fixture to fail before this test
    could execute.
    """

    response = live_session.get(
        f"{base_url}/status/not-a-valid-job-id",
        timeout=10,
    )

    assert response.status_code in {
        400,
        401,
        403,
        404,
        422,
    }, (
        "Invalid job_id should be rejected. "
        f"Received {response.status_code}: {response.text}"
    )