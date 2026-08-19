import pytest


pytestmark = pytest.mark.dynamic


def response_schema(openapi, method, path, status_code="200"):
    operation = openapi["paths"][path][method.lower()]
    response = operation["responses"][status_code]

    return (
        response
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )


def request_schema(openapi, method, path):
    operation = openapi["paths"][path][method.lower()]

    request_body = operation.get("requestBody", {})

    return (
        request_body
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )


def assert_required_properties(schema, expected):
    """
    Verify that the schema exposes the expected required properties.
    """
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    missing_properties = expected - set(properties)

    assert not missing_properties, (
        f"Schema is missing properties: "
        f"{sorted(missing_properties)}"
    )

    missing_required = expected - required

    assert not missing_required, (
        f"Expected properties are not marked required: "
        f"{sorted(missing_required)}"
    )


def test_root_response_contract(live_session, base_url):
    response = live_session.get(
        f"{base_url}/",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("status") == "success"
    assert data.get("message")


def test_health_response_contract(live_session, base_url):
    response = live_session.get(
        f"{base_url}/health",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    required = {
        "gateway",
        "player_service",
        "crowd_service",
    }

    assert required.issubset(data)

    assert data["gateway"] in {
        "ok",
        "error",
        "unreachable",
        "pending",
    }

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


def test_root_openapi_response_contract(openapi):
    schema = response_schema(
        openapi,
        "GET",
        "/",
    )

    assert schema, "GET / does not document a JSON response schema"

    assert_required_properties(
        schema,
        {
            "status",
            "message",
        },
    )


def test_health_openapi_response_contract(openapi):
    schema = response_schema(
        openapi,
        "GET",
        "/health",
    )

    assert schema, (
        "GET /health does not document a JSON response schema"
    )

    assert_required_properties(
        schema,
        {
            "gateway",
            "player_service",
            "crowd_service",
        },
    )


def test_register_request_contract(openapi):
    schema = request_schema(
        openapi,
        "POST",
        "/auth/register",
    )

    assert_required_properties(
        schema,
        {
            "username",
            "email",
            "password",
        },
    )


def test_login_request_contract(openapi):
    schema = request_schema(
        openapi,
        "POST",
        "/auth/login",
    )

    assert_required_properties(
        schema,
        {
            "email",
            "password",
        },
    )


def test_refresh_request_contract(openapi):
    schema = request_schema(
        openapi,
        "POST",
        "/auth/refresh",
    )

    assert_required_properties(
        schema,
        {
            "refresh_token",
        },
    )


def test_logout_request_contract(openapi):
    schema = request_schema(
        openapi,
        "POST",
        "/auth/logout",
    )

    assert_required_properties(
        schema,
        {
            "refresh_token",
        },
    )


def test_auth_response_contract(openapi):
    schema = response_schema(
        openapi,
        "POST",
        "/auth/register",
    )

    properties = schema.get("properties", {})

    expected = {
        "access_token",
        "refresh_token",
        "token_type",
        "expires_in",
        "user",
    }

    missing = expected - set(properties)

    assert not missing, (
        "Authentication response contract is missing: "
        f"{sorted(missing)}"
    )


def test_upload_request_is_multipart(openapi):
    operation = openapi["paths"]["/upload"]["post"]

    content = (
        operation
        .get("requestBody", {})
        .get("content", {})
    )

    assert "multipart/form-data" in content, (
        "POST /upload must accept multipart/form-data"
    )

    schema = content["multipart/form-data"].get("schema", {})
    properties = schema.get("properties", {})

    assert "file" in properties, (
        "POST /upload is missing the 'file' request field"
    )


def test_upload_response_contract(openapi):
    schema = response_schema(
        openapi,
        "POST",
        "/upload",
    )

    assert schema, (
        "POST /upload does not document a JSON response"
    )

    properties = schema.get("properties", {})

    assert "job_id" in properties
    assert "status" in properties


def test_job_status_path_parameter_is_uuid(openapi):
    parameter = None

    for candidate in openapi["paths"]["/status/{job_id}"].get(
        "parameters",
        [],
    ):
        if (
            candidate.get("name") == "job_id"
            and candidate.get("in") == "path"
        ):
            parameter = candidate
            break

    assert parameter is not None, (
        "/status/{job_id} must declare job_id as a path parameter"
    )

    schema = parameter.get("schema", {})

    assert schema.get("format") == "uuid", (
        "/status/{job_id} should use a UUID path parameter"
    )


def test_jobs_pagination_contract(openapi):
    operation = openapi["paths"]["/jobs"]["get"]

    parameters = {
        parameter["name"]: parameter
        for parameter in operation.get("parameters", [])
    }

    assert "page" in parameters
    assert "limit" in parameters

    assert parameters["page"]["in"] == "query"
    assert parameters["limit"]["in"] == "query"


def test_protected_endpoint_rejects_missing_token(
    live_session,
    base_url,
):
    response = live_session.get(
        f"{base_url}/auth/me",
        timeout=5,
    )

    assert response.status_code == 401

    data = response.json()

    assert "detail" in data


def test_invalid_job_id_is_rejected(
    live_session,
    base_url,
    registered_user,
):
    token = registered_user["data"]["access_token"]

    response = live_session.get(
        f"{base_url}/status/not-a-valid-uuid",
        headers={
            "Authorization": f"Bearer {token}",
        },
        timeout=5,
    )

    assert response.status_code == 400

    data = response.json()

    assert "detail" in data