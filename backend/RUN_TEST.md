# Orion Dynamic Backend Testing

## 1. Purpose

The `dynamic_tests` suite provides live backend testing for Project Orion.

Unlike the existing `tests/` directory, which primarily uses mocked dependencies and FastAPI's `TestClient`, the dynamic suite communicates with a running Orion backend through HTTP.

The dynamic suite checks:

- OpenAPI availability
- endpoint discovery
- endpoint regression
- API security documentation
- request and response contracts
- authentication workflows
- protected endpoint behaviour
- video upload behaviour
- job creation
- downstream service failure handling
- live backend health

---

## 2. Directory Structure

```text
Backend/
├── app/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
|   ├── test_auth.py
│   ├── test_health.py
│   ├── test_jobs.py
│   └── test_upload.py
│
├── dynamic_tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_contract_validation.py
│   ├── test_live_integration.py
│   ├── test_openapi_dynamic.py
│   └── test_service_failure_dynamic.py
│
├── requirements.txt
├── requirements-test.txt
├── pytest.ini
└── RUN_TESTS.md