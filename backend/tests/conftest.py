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
from .fakes import FakeAuthService, FakeUserService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends


# FakeAuthService and FakeUserService moved to backend/tests/fakes.py


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
