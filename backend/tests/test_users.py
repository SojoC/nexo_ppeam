def test_users_crud(client):
    # Crear un usuario
    user_data = {
        "nombre": "Juan Pérez",
        "telefono": "1234567890",
        "ciudad": "Caracas",
        "congregacion": "Centro",
        "privilegio": "Publicador",
        "email": "juan@example.com",
    }
    r = client.post("/api/v2/users", json=user_data)
    assert r.status_code in (200, 201)
    created = r.json()
    user_id = created.get("id")
    assert user_id

    # Obtener el usuario por ID
    r = client.get(f"/api/v2/users/{user_id}")
    assert r.status_code == 200
    assert r.json().get("nombre") == "Juan Pérez"

    # Actualizar el usuario (cambiar ciudad)
    r = client.put(f"/api/v2/users/{user_id}", json={"ciudad": "Valencia"})
    assert r.status_code == 200
    assert r.json().get("ciudad") == "Valencia"

    # Eliminar (soft delete)
    r = client.delete(f"/api/v2/users/{user_id}")
    assert r.status_code == 200
    # Depending on implementation, check response type or active flag
    body = r.json()
    assert body.get("type") == "soft_delete" or body.get("active") is False


def test_change_password(client):
    # Registramos y logueamos
    email = "change@example.com"
    password = "oldpass"
    new_password = "newpass"
    client.post("/api/v2/auth/register", json={"email": email, "password": password})
    r = client.post("/api/v2/auth/login", json={"email": email, "password": password})
    token = r.json()["access_token"]

    # Cambiar la contraseña
    r = client.post(
        "/api/v2/auth/change-password",
        json={"current_password": password, "new_password": new_password},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200

    # Verificar que la nueva contraseña funciona
    r = client.post("/api/v2/auth/login", json={"email": email, "password": new_password})
    assert r.status_code == 200


def test_user_not_found_returns_404(client):
    r = client.get("/api/v2/users/non-existent-id")
    assert r.status_code == 404


def test_conflict_on_duplicate_email_and_phone(client):
    user1 = {
        "nombre": "Ana",
        "telefono": "5550001",
        "ciudad": "CiudadA",
        "congregacion": "CongA",
        "privilegio": "Publicador",
        "email": "ana@example.com",
    }
    r = client.post("/api/v2/users", json=user1)
    assert r.status_code in (200, 201)

    # Mismo email -> 409
    user_dup_email = user1.copy()
    user_dup_email["telefono"] = "5550002"
    r = client.post("/api/v2/users", json=user_dup_email)
    assert r.status_code == 409

    # Mismo teléfono -> 409
    user_dup_phone = user1.copy()
    user_dup_phone["email"] = "another@example.com"
    r = client.post("/api/v2/users", json=user_dup_phone)
    assert r.status_code == 409


def test_list_filters_and_stats(client):
    # Crear varios usuarios
    users = [
        {"nombre": "U1", "ciudad": "C1", "congregacion": "G1", "telefono": "9001", "email": "u1@example.com"},
        {"nombre": "U2", "ciudad": "C1", "congregacion": "G2", "telefono": "9002", "email": "u2@example.com"},
        {"nombre": "U3", "ciudad": "C2", "congregacion": "G1", "telefono": "9003", "email": "u3@example.com"},
    ]
    for u in users:
        r = client.post("/api/v2/users", json=u)
        assert r.status_code in (200, 201)

    # Filtrar por ciudad C1 -> debe devolver 2 usuarios
    r = client.get("/api/v2/users", params={"ciudad": "C1", "per_page": 50})
    assert r.status_code == 200
    body = r.json()
    assert body.get("total") >= 2

    # Stats generales
    r = client.get("/api/v2/users/stats/general")
    assert r.status_code == 200
    stats = r.json()
    assert stats.get("total_usuarios") >= 3
    assert "congregaciones" in stats
