# Pruebas de backend de Nexo_PPEAM

Este directorio contiene la suite de tests para el backend. Las pruebas usan un `FakeAuthService` y un
`FakeUserService` definidos en `conftest.py` para evitar dependencias externas (Firestore, SMS, etc.).

## Requisitos

- Python 3.11 o superior.
- Un entorno virtual activo (recomendado).
- Dependencias listadas en:
  - `backend/requirements.txt` – dependencias de la aplicación.
  - `backend/requirements-tests.txt` – dependencias de testing (pytest y otras).

## Configuración rápida

1. Crear un entorno virtual y activarlo:

   En macOS / Linux:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   En Windows (PowerShell):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Instalar las dependencias:

```bash
pip install -r backend/requirements.txt
pip install -r backend/requirements-tests.txt
```

3. Ejecutar las pruebas:

```bash
pytest
```

PyTest utilizará automáticamente la configuración de `pytest.ini` (ejecución en `backend/tests` y salida en modo verbose).

## Estructura de pruebas

- `conftest.py` define los fixtures y los servicios en memoria (`FakeAuthService`, `FakeUserService`).
- `test_smoke.py` valida el flujo básico de autenticación (register → login → /auth/me).
- `test_users.py` cubre el CRUD de usuarios, manejo de errores (404/409), filtros y estadísticas.

Para cualquier duda adicional, consulta los comentarios en cada archivo o la documentación del proyecto.

## Git (añadir README)

Para añadir y publicar este README:

```bash
git add backend/tests/README.md
git commit -m "docs: añadir README de tests con instrucciones de ejecución"
git push origin master
```
