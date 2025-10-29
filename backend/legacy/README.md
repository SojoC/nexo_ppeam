Legacy routers y módulos
=========================

Este directorio contiene versiones "legacy" de routers y módulos que fueron
movidos desde `backend/routes/` para limpiar y consolidar la API v2.

Motivo:
- Evitar solapamientos entre rutas v1 (legacy) y v2 mientras se realiza la
  migración y refactorización.
- Mantener el código para referencia o para restaurarlo si es necesario.

Archivos movidos:
- routes/contacts_firebase.py
- routes/messages.py
- routes/campaigns.py
- routes/realtime.py

Cómo restaurar:
1. Mover los archivos de vuelta a `backend/routes/`.
2. Descomentar las inclusiones en `backend/main_v2.py` o `backend/app.py`.

Nota: Estos módulos pueden depender de modelos/repositories que siguen presentes
en `backend/models` y `backend/repository`. Antes de restaurar, verifica compatibilidad.
