from fastapi.testclient import TestClient
from main_v2 import app

# Import the dependency key to override (function defined in services.auth_service)
from services.auth_service import get_auth_service


class FakeAuthService:
    """Servicio falso para tests que simula register/login/me sin Firestore."""

    async def register_user(self, email: str, password: str, display_name=None):
        return {
            "id": email,
            "email": email,
            "display_name": display_name or "Test User",
            "provider": "password",
            "role": "user",
        }

    async def login_user(self, email: str, password: str):
        # Devuelve un token fijo para pruebas
        return {
            "access_token": "fake-token-for-" + email,
            "token_type": "bearer",
        }

    async def get_user_by_token(self, token_subject: str):
        # token_subject será el subject decodificado por core.security (ej: email)
        return {
            "id": token_subject,
            "email": token_subject,
            "display_name": "Test User",
            "provider": "password",
            "role": "user",
            "active": True,
        }


# Fixture: TestClient con override de dependencia
client = TestClient(app)
app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") in ("healthy", "unhealthy")


def test_register_login_me_flow():
    email = "test@example.com"
    password = "secret123"

    # Registrar
    r = client.post("/api/v2/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == email

    # Login
    r = client.post("/api/v2/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token and token.startswith("fake-token-for-")

    # /me (usa dependencia get_current_user que en este test usará el subject)
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v2/auth/me", headers=headers)
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == email
