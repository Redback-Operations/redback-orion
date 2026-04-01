import uuid
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db


@pytest.fixture
def mock_db():
    db = MagicMock()
    # Default: no existing user found
    db.query.return_value.filter.return_value.first.return_value = None

    def refresh_side_effect(obj):
        if not getattr(obj, "user_id", None):
            obj.user_id = uuid.uuid4()
        if not getattr(obj, "role", None):
            obj.role = "user"
        if not getattr(obj, "created_at", None):
            obj.created_at = datetime.now(timezone.utc)

    db.refresh.side_effect = refresh_side_effect
    return db


@pytest.fixture
def client(mock_db):
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
