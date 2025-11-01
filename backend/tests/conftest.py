import os
import sys
import pytest

# Las modificaciones de sys.path y cwd ahora se realizan en
# backend/tests/__init__.py para no alterar el comportamiento de las fixtures.

from fastapi.testclient import TestClient
from main_v2 import app
from services.auth_service import get_auth_service
from services.user_service import get_user_service
from core import security as core_security
from core.exceptions import NotFoundError, ConflictError, AuthenticationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends


class FakeAuthService:
    """Servicio de autenticación en memoria para pruebas (compartido)."""

    def __init__(self):
        self.users = {}

    async def register_user(self, email: str, password: str, display_name: str = None):
        email = email.lower()
        if email in self.users:
            raise ConflictError(f"Email {email} ya existe")
        self.users[email] = {
            "id": email,
            "email": email,
            "display_name": display_name or "",
            "provider": "password",
            "role": "user",
            "password": password,
            "active": True,
        }
        return {
            "id": email,
            "email": email,
            "display_name": self.users[email]["display_name"],
            "provider": "password",
            "role": "user",
        }

    async def login_user(self, email: str, password: str):
        email = email.lower()
        u = self.users.get(email)
        if not u or u.get("password") != password:
            raise AuthenticationError("Credenciales inválidas")
        from core.security import create_access_token
        token = create_access_token(subject=email)
        return {"access_token": token, "token_type": "bearer"}

    async def get_user_by_token(self, token_subject: str):
        u = self.users.get(token_subject)
        if not u:
            return None
        return {
            "id": u["id"],
            "email": u["email"],
            "display_name": u["display_name"],
            "provider": u["provider"],
            "role": u["role"],
            "active": u["active"],
        }

    async def change_password(self, email: str, current_password: str, new_password: str):
        """Cambiar contraseña en el servicio fake (simple comprobación)."""
        email = email.lower()
        u = self.users.get(email)
        if not u:
            raise NotFoundError("Usuario")
        if u.get("password") != current_password:
            raise AuthenticationError("Contraseña actual incorrecta")
        u["password"] = new_password
        return True


class FakeUserService:
    """Servicio de usuarios en memoria para pruebas."""

    def __init__(self):
        # store by id
        self.users = {}

    async def create_user(self, user_data: dict, created_by: str = None):
        # Use email as id if present, otherwise generate
        email = (user_data.get("email") or "").lower()
        # Verificar conflicto por email o teléfono
        if email:
            # si ya existe email -> conflicto
            for u in self.users.values():
                if (u.get("email") or "").lower() == email:
                    raise ConflictError(f"Email {email} ya existe")
            user_id = email
        else:
            # generar id incremental
            user_id = f"user-{len(self.users) + 1}"
        phone = user_data.get("telefono")
        if phone:
            for u in self.users.values():
                if u.get("telefono") == phone:
                    raise ConflictError(f"Teléfono {phone} ya existe")

        user = {
            "id": user_id,
            "nombre": user_data.get("nombre", ""),
            "edad": user_data.get("edad"),
            "fecha_nacimiento": user_data.get("fecha_nacimiento"),
            "sexo": user_data.get("sexo"),
            "estado_civil": user_data.get("estado_civil"),
            "fecha_bautismo": user_data.get("fecha_bautismo"),
            "privilegio": user_data.get("privilegio"),
            "telefono": user_data.get("telefono"),
            "congregacion": user_data.get("congregacion"),
            "ciudad": user_data.get("ciudad"),
            "email": email or None,
            "active": True,
            "created_at": None,
            "updated_at": None,
        }
        self.users[user_id] = user
        return user

    async def list_users(self, limit: int, offset: int, congregacion=None, ciudad=None, privilegio=None, active_only=True, search=None):
        users = list(self.users.values())
        if active_only:
            users = [u for u in users if u.get("active", True)]
        if congregacion:
            users = [u for u in users if u.get("congregacion") == congregacion]
        if ciudad:
            users = [u for u in users if u.get("ciudad") == ciudad]
        if privilegio:
            users = [u for u in users if u.get("privilegio") == privilegio]
        if search:
            users = [u for u in users if search.lower() in (u.get("nombre") or "").lower() or search.lower() in (u.get("email") or "").lower()]
        total = len(users)
        sliced = users[offset: offset + limit]
        return sliced, total

    async def get_user(self, user_id: str):
        u = self.users.get(user_id)
        if not u:
            raise NotFoundError("Usuario")
        return u

    async def update_user(self, user_id: str, update_data: dict, updated_by: str = None):
        u = self.users.get(user_id)
        if not u:
            raise NotFoundError("Usuario")
        u.update(update_data)
        return u

    async def delete_user(self, user_id: str, soft_delete: bool = True):
        u = self.users.get(user_id)
        if not u:
            raise NotFoundError("Usuario")
        if soft_delete:
            u["active"] = False
        else:
            del self.users[user_id]
        return True

    async def get_user_by_email(self, email: str):
        email = email.lower()
        for u in self.users.values():
            if (u.get("email") or "").lower() == email:
                return u
        return None

    async def get_user_by_phone(self, phone: str):
        for u in self.users.values():
            if u.get("telefono") == phone:
                return u
        return None

    async def get_user_stats(self):
        total = len([u for u in self.users.values() if u.get("active", True)])
        congregaciones = {}
        ciudades = {}
        privilegios = {}
        por_sexo = {}
        for u in self.users.values():
            if not u.get("active", True):
                continue
            congregaciones[u.get("congregacion") or "Sin congregación"] = congregaciones.get(u.get("congregacion") or "Sin congregación", 0) + 1
            ciudades[u.get("ciudad") or "Sin ciudad"] = ciudades.get(u.get("ciudad") or "Sin ciudad", 0) + 1
            privilegios[u.get("privilegio") or "Sin privilegio"] = privilegios.get(u.get("privilegio") or "Sin privilegio", 0) + 1
            por_sexo[u.get("sexo") or "Desconocido"] = por_sexo.get(u.get("sexo") or "Desconocido", 0) + 1

        return {
            "total_usuarios": total,
            "congregaciones": congregaciones,
            "ciudades": ciudades,
            "privilegios": privilegios,
            "por_sexo": por_sexo,
        }


@pytest.fixture(scope="session")
def fake_user_service():
    return FakeUserService()



@pytest.fixture(scope="session")
def fake_auth_service():
    """Servicio fake reutilizable por sesión de test."""
    return FakeAuthService()


@pytest.fixture
def client(fake_auth_service, fake_user_service):
    """TestClient con dependencias sobrescritas para pruebas HTTP."""
    app.dependency_overrides[get_auth_service] = lambda: fake_auth_service
    app.dependency_overrides[get_user_service] = lambda: fake_user_service

    def fake_get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):
        token = credentials.credentials
        if token.startswith("fake-token:"):
            return token.split(":", 1)[1]
        return core_security.decode_access_token(token)

    app.dependency_overrides[core_security.get_current_user] = fake_get_current_user

    with TestClient(app) as c:
        yield c

    # Limpiar overrides para no contaminar otras pruebas
    app.dependency_overrides.clear()
