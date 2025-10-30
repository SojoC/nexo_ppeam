import pytest


def test_register_login_me(client):
    email = "test@example.com"
    password = "123456"

    # Registrar
    r = client.post("/api/v2/auth/register", json={"email": email, "password": password})
    assert r.status_code in (200, 201)

    # Login y token
    r = client.post("/api/v2/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    token = r.json()["access_token"]

    # /me debe responder 200 con los datos del usuario
    r = client.get("/api/v2/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == email
