import os
import sys

# Ajustes de entorno para que las pruebas se ejecuten desde la carpeta backend
# Esto se ejecuta cuando pytest importa el paquete backend.tests antes de los módulos
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Establecer el cwd a backend para que Pydantic cargue backend/.env en lugar del .env raíz
try:
    os.chdir(ROOT)
except Exception:
    # No bloquear si por alguna razón no se puede cambiar (por ejemplo permisos)
    pass
