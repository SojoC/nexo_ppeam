"""Runner ligero de smoke tests sin depender de pytest.

Este script ejecuta comprobaciones básicas de la API v2 usando TestClient.
Es útil en entornos donde pytest no está instalado.
"""
import sys
from fastapi.testclient import TestClient
from main_v2 import app
from services.auth_service import get_auth_service
from core.security import get_current_user


class FakeAuthService:
    async def register_user(self, email: str, password: str, display_name=None):
        return {
            "id": email,
            "email": email,
            "display_name": display_name or "Test User",
            "provider": "password",
            "role": "user",
        }

    async def login_user(self, email: str, password: str):
        return {"access_token": "fake-token-for-" + email, "token_type": "bearer"}

    async def get_user_by_token(self, token_subject: str):
        return {
            "id": token_subject,
            "email": token_subject,
            "display_name": "Test User",
            "provider": "password",
            "role": "user",
            "active": True,
        }


def run():
    print("Iniciando smoke tests...")
    client = TestClient(app)
    # Override the AuthService to avoid usar Firestore
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    # Inicialmente dejamos get_current_user en su estado normal; tras el login
    # sobreescribiremos la dependencia para devolver directamente el email de prueba
    # (esto evita depender de la decodificación JWT en el entorno de pruebas).
    # Nota: hacemos la sobreescritura después de obtener el token.

    # Health
    r = client.get("/health")
    if r.status_code != 200:
        print("FAIL: /health status", r.status_code, r.text)
        return 2
    print("OK: /health ->", r.json().get("status"))

    # Register
    email = "smoke@example.com"
    password = "secret123"
    r = client.post("/api/v2/auth/register", json={"email": email, "password": password})
    if r.status_code != 201:
        print("FAIL: register", r.status_code, r.text)
        return 3
    print("OK: register ->", r.json().get("email"))

    # Login
    r = client.post("/api/v2/auth/login", json={"email": email, "password": password})
    if r.status_code != 200:
        print("FAIL: login", r.status_code, r.text)
        return 4
    token = r.json().get("access_token")
    print("OK: login -> token len", len(token or ""))

    # Me
    # Ahora sobreescribimos la dependencia get_current_user para que devuelva
    # directamente el email de prueba (evitamos decodificar el JWT en tests)
    app.dependency_overrides[get_current_user] = lambda credentials=None: email

    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v2/auth/me", headers=headers)
    if r.status_code != 200:
        print("FAIL: /auth/me", r.status_code, r.text)
        return 5
    print("OK: /auth/me ->", r.json().get("email"))

    print("All smoke checks passed.")
    return 0


if __name__ == '__main__':
    code = run()
    sys.exit(code)
