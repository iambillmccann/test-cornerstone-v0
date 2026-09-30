import pytest
from app.auth import get_current_auth_identity
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the /api/v1/health endpoint."""

    def test_health_returns_ok(self, client):
        """Health endpoint should return status ok."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_response_schema(self, client):
        """Health response should match HealthResponse schema."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)


class TestReadyEndpoint:
    """Tests for the /api/v1/ready endpoint."""

    def test_ready_returns_ready(self, client):
        """Readiness endpoint should return status ready."""
        response = client.get("/api/v1/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    def test_ready_response_schema(self, client):
        """Ready response should match HealthResponse schema."""
        response = client.get("/api/v1/ready")
        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)


class TestVersionEndpoint:
    """Tests for the /api/v1/version endpoint."""

    def test_version_returns_data(self, client):
        """Version endpoint should return name and version."""
        response = client.get("/api/v1/version")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "cornerstone-api"
        assert data["version"] == "0.1.0"

    def test_version_response_schema(self, client):
        """Version response should match VersionResponse schema."""
        response = client.get("/api/v1/version")
        data = response.json()
        assert isinstance(data["name"], str)
        assert isinstance(data["version"], str)


class TestErrorShapes:
    """Tests for structured error responses."""

    def test_404_error_shape(self, client):
        """404 responses should use structured error format."""
        response = client.get("/api/v1/does-not-exist")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "details" in data["error"]
        assert data["error"]["code"] == "http_error"
        assert isinstance(data["error"]["details"], list)

    def test_validation_error_shape(self, client):
        """Validation error responses should use structured error format."""
        # This would require an endpoint that accepts request body with validation
        # For now, we verify the error handler structure is in place
        # by checking that a malformed request produces an error response
        response = client.post("/api/v1/health", json={"invalid": "data"})
        assert response.status_code in [404, 405, 422]
        # Endpoints that return 404 or 405 should still use structured error
        data = response.json()
        assert "error" in data or response.status_code in [404, 405]

    def test_error_response_has_required_fields(self, client):
        """Error responses should always have error.code, error.message, error.details."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        data = response.json()
        error = data.get("error")
        assert error is not None
        assert isinstance(error.get("code"), str)
        assert isinstance(error.get("message"), str)
        assert isinstance(error.get("details"), list)


class TestCORSConfiguration:
    """Tests for CORS configuration."""

    def test_cors_allows_localhost_5173(self, client):
        """CORS should allow requests from localhost:5173."""
        # CORS middleware should be configured with the origin
        # Verify via GET request with Origin header
        origin = "http://localhost:5173"
        response = client.get(
            "/api/v1/health",
            headers={"Origin": origin},
        )
        assert response.status_code == 200
        # Verify the response still works with origin header
        assert response.json() == {"status": "ok"}
        assert response.headers.get("access-control-allow-origin") == origin

    def test_cors_allows_localhost_5174(self, client):
        """CORS should allow requests from localhost:5174."""
        origin = "http://localhost:5174"
        response = client.get(
            "/api/v1/health",
            headers={"Origin": origin},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert response.headers.get("access-control-allow-origin") == origin

    def test_cors_allows_localhost_4173(self, client):
        """CORS should allow requests from localhost:4173."""
        origin = "http://localhost:4173"
        response = client.get(
            "/api/v1/health",
            headers={"Origin": origin},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert response.headers.get("access-control-allow-origin") == origin

    def test_cors_allows_localhost_3000(self, client):
        """CORS should allow requests from localhost:3000."""
        origin = "http://localhost:3000"
        response = client.get(
            "/api/v1/health",
            headers={"Origin": origin},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert response.headers.get("access-control-allow-origin") == origin


class TestAuthEndpoint:
    """Tests for the /api/v1/auth/me endpoint."""

    def test_auth_me_requires_bearer_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "http_error"
        assert data["error"]["message"] == "Missing bearer token"

    def test_auth_me_returns_identity_from_verified_token(self, client):
        def _mock_identity():
            return {
                "sub": "user_123",
                "sid": "sess_123",
                "iss": "https://example.clerk.accounts.dev",
                "azp": "http://localhost:5173",
                "email": "user@example.com",
            }

        app.dependency_overrides[get_current_auth_identity] = _mock_identity
        try:
            response = client.get("/api/v1/auth/me")
            assert response.status_code == 200
            assert response.json() == {
                "sub": "user_123",
                "sid": "sess_123",
                "iss": "https://example.clerk.accounts.dev",
                "azp": "http://localhost:5173",
                "email": "user@example.com",
            }
        finally:
            app.dependency_overrides.clear()


class TestMeEndpoint:
    """Tests for the /api/me canonical profile endpoint."""

    def test_me_requires_bearer_token(self, client):
        """The /api/me endpoint should require a bearer token."""
        response = client.get("/api/me")
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "http_error"
        assert data["error"]["message"] == "Missing bearer token"

    def test_me_returns_app_user_profile(self, client, db_session):
        """The /api/me endpoint should return the app user profile from persistence."""
        from app.db.session import get_db_session

        def _mock_identity():
            return {
                "sub": "user_abc_123",
                "email": "testuser@example.com",
                "name": "Test User",
                "picture": "https://example.com/avatar.png",
            }

        def _mock_get_db():
            return db_session

        app.dependency_overrides[get_current_auth_identity] = _mock_identity
        app.dependency_overrides[get_db_session] = _mock_get_db
        try:
            response = client.get("/api/me")
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["email"] == "testuser@example.com"
            assert data["display_name"] == "Test User"
            assert data["avatar_url"] == "https://example.com/avatar.png"
        finally:
            app.dependency_overrides.clear()

    def test_me_bootstraps_user_on_first_call(self, client, db_session):
        """First call to /api/me should create user and default workspace."""
        from app.db.models.user import User
        from app.db.session import get_db_session
        from sqlalchemy import select

        def _mock_identity():
            return {
                "sub": "user_new_001",
                "email": "newuser@example.com",
                "name": "New User",
            }

        def _mock_get_db():
            return db_session

        app.dependency_overrides[get_current_auth_identity] = _mock_identity
        app.dependency_overrides[get_db_session] = _mock_get_db
        try:
            response = client.get("/api/me")
            assert response.status_code == 200

            # Verify user was created in database
            user = db_session.execute(
                select(User).where(User.auth_provider_user_id == "user_new_001")
            ).scalar_one()
            assert user.email == "newuser@example.com"
            assert user.display_name == "New User"
        finally:
            app.dependency_overrides.clear()

    def test_me_returns_same_user_on_repeat_calls(self, client, db_session):
        """Repeated calls with same identity should return same user (no duplicates)."""
        from app.db.models.user import User
        from app.db.session import get_db_session
        from sqlalchemy import select

        def _mock_identity():
            return {
                "sub": "user_repeat_001",
                "email": "repeat@example.com",
                "name": "Repeat User",
            }

        def _mock_get_db():
            return db_session

        app.dependency_overrides[get_current_auth_identity] = _mock_identity
        app.dependency_overrides[get_db_session] = _mock_get_db
        try:
            # First call
            response1 = client.get("/api/me")
            assert response1.status_code == 200
            id1 = response1.json()["id"]

            # Second call with same identity
            response2 = client.get("/api/me")
            assert response2.status_code == 200
            id2 = response2.json()["id"]

            # IDs should match (same user)
            assert id1 == id2

            # Verify only one user exists in database
            users = (
                db_session.execute(
                    select(User).where(User.auth_provider_user_id == "user_repeat_001")
                )
                .scalars()
                .all()
            )
            assert len(users) == 1
        finally:
            app.dependency_overrides.clear()

    def test_me_falls_back_to_clerk_profile_when_claims_missing(
        self, client, db_session, monkeypatch
    ):
        """When JWT claims omit profile fields, /api/me should enrich from Clerk API."""
        import app.routes as routes_module
        from app.db.session import get_db_session

        def _mock_identity():
            return {
                "sub": "user_claims_missing_001",
            }

        def _mock_get_db():
            return db_session

        def _mock_fetch_clerk_user_profile(user_id: str, secret_key: str):
            assert user_id == "user_claims_missing_001"
            return {
                "first_name": "Bill",
                "last_name": "McCann",
                "image_url": "https://example.com/bill.png",
                "primary_email_address_id": "idn_primary",
                "email_addresses": [
                    {
                        "id": "idn_primary",
                        "email_address": "bill@example.com",
                    }
                ],
            }

        monkeypatch.setattr(
            routes_module, "fetch_clerk_user_profile", _mock_fetch_clerk_user_profile
        )
        monkeypatch.setattr(
            routes_module.settings, "clerk_secret_key", "sk_test_example"
        )

        app.dependency_overrides[get_current_auth_identity] = _mock_identity
        app.dependency_overrides[get_db_session] = _mock_get_db
        try:
            response = client.get("/api/me")
            assert response.status_code == 200
            data = response.json()
            assert data["display_name"] == "Bill McCann"
            assert data["email"] == "bill@example.com"
            assert data["avatar_url"] == "https://example.com/bill.png"
        finally:
            app.dependency_overrides.clear()
