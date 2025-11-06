# Cómo ejecutar (rápido)

Resumen rápido para arrancar el proyecto en tu máquina y URLs de acceso.

1) Levantar todo con Docker (producción ligera / preview):

PowerShell (desde la raíz del repo):

```powershell
docker compose up --build -d
```

- Frontend (nginx que sirve la build): http://localhost:3000
- Backend (FastAPI / uvicorn): http://localhost:8000
  - Health: http://localhost:8000/health
  - Docs (OpenAPI): http://localhost:8000/docs

Notas:
- En el contenedor, el frontend se sirve por nginx en el puerto 80 del container y está mapeado al puerto 3000 del host. Si estabas intentando `http://localhost:5173` eso corresponde al dev server de Vite (solo si ejecutas `npm run dev` localmente), no al contenedor.

2) Desarrollo local (sin Docker):

Backend (usa el virtualenv del repositorio `.venv`):

```powershell
Set-Location C:\Nexo_PPAM\nexo_ppeam
& .venv\Scripts\Activate.ps1
uvicorn backend.app:app --reload --port 8000
```

Frontend (Vite dev server):

```powershell
Set-Location C:\Nexo_PPAM\nexo_ppeam\frontend
npm ci
npm run dev
# abre: http://localhost:5173
```

3) Ejecutar tests (desde la raíz):

```powershell
Set-Location C:\Nexo_PPAM\nexo_ppeam
& .venv\Scripts\Activate.ps1
python -m pytest -q
```

Resultado esperado (local): "8 passed" (los tests existentes pasan, hay warnings por Pydantic y datetime que se pueden migrar en una siguiente tarea).

4) Logs (útiles para debugging):

```powershell
# ver estado de containers
docker compose ps

# ver logs (últimas líneas)
docker compose logs --tail 200

# seguir logs en tiempo real
docker compose logs -f
```

Si quieres, creo una rama `fix/run-all` que:
- añade este `RUNNING.md` (ya creado)
- añade una nota en `frontend/README.md` y/o un script `scripts/start-dev.ps1` para un arranque dev más sencillo
- opcionalmente expone el puerto 5173 en `docker-compose` para desarrolladores (si prefieres trabajar con Vite dentro de Docker)

Dime si quieres que haga esos cambios automáticos y abra el PR; si no, con lo anterior ya tienes la aplicación corriendo en Docker y los tests verdes.
