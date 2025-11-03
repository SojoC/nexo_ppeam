from typing import List

from fastapi.testclient import TestClient


def make_user(i: int):
    return {
        "nombre": f"User {i}",
        "telefono": f"700{i:03d}",
        "ciudad": "CTest",
        # Usar congregacion única para aislar los tests de otros usuarios creados
        "congregacion": "GTestPagination",
        "privilegio": "Publicador",
        "email": f"user{i}@example.com",
    }


def test_users_pagination_returns_correct_pages(client: TestClient):
    # crear 12 usuarios
    total_to_create = 12
    created_ids: List[str] = []
    for i in range(1, total_to_create + 1):
        r = client.post("/api/v2/users", json=make_user(i))
        assert r.status_code in (200, 201)
        created = r.json()
        created_ids.append(created.get("id"))

    # Page 1, per_page 5 (filtrando por congregacion para aislar los usuarios creados)
    params = {"per_page": 5, "page": 1, "congregacion": "GTestPagination"}
    r = client.get("/api/v2/users", params=params)
    assert r.status_code == 200
    body = r.json()
    assert body.get("per_page") == 5
    assert body.get("page") == 1
    assert body.get("total") >= total_to_create
    users_page1 = body.get("users")
    assert isinstance(users_page1, list)
    assert len(users_page1) == 5

    # Page 2
    params["page"] = 2
    r = client.get("/api/v2/users", params=params)
    assert r.status_code == 200
    body2 = r.json()
    users_page2 = body2.get("users")
    assert isinstance(users_page2, list)
    assert len(users_page2) == 5

    # Page 3 should contain the remainder (2)
    params["page"] = 3
    r = client.get("/api/v2/users", params=params)
    assert r.status_code == 200
    body3 = r.json()
    users_page3 = body3.get("users")
    assert isinstance(users_page3, list)
    assert len(users_page3) == total_to_create - 10

    # Ensure no duplicates across pages by comparing ids
    ids_seen = {u.get("id") for u in users_page1 + users_page2 + users_page3}
    assert len(ids_seen) == total_to_create


def test_users_search_by_name_and_email(client: TestClient):
    # Clean-ish namespace by creating uniquely named users
    users = [
        {"nombre": "Alice Search", "telefono": "8010", "ciudad": "S1", "congregacion": "G1", "privilegio": "Publicador", "email": "alice.search@example.com"},
        {"nombre": "Bob", "telefono": "8011", "ciudad": "S1", "congregacion": "G1", "privilegio": "Publicador", "email": "bob@example.com"},
        {"nombre": "Carol", "telefono": "8012", "ciudad": "S1", "congregacion": "G1", "privilegio": "Publicador", "email": "carol.search@example.com"},
    ]

    for u in users:
        r = client.post("/api/v2/users", json=u)
        assert r.status_code in (200, 201)

    # Search by name fragment 'Alice'
    r = client.get("/api/v2/users", params={"search": "Alice"})
    assert r.status_code == 200
    body = r.json()
    results = body.get("users")
    assert any("Alice" in (u.get("nombre") or "") for u in results)

    # Search by email fragment 'search' should match both alice and carol
    r = client.get("/api/v2/users", params={"search": "search"})
    assert r.status_code == 200
    body2 = r.json()
    results2 = body2.get("users")
    emails = [u.get("email") for u in results2]
    assert "alice.search@example.com" in emails
    assert "carol.search@example.com" in emails
