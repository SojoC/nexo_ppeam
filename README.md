# Nexo PPEAM

Aplicación de gestión de contactos y campañas de mensajería con FastAPI backend y React frontend.

## Arquitectura

- **Backend**: FastAPI + Uvicorn (Python 3.12)
- **Frontend**: React + TypeScript + Vite
- **Base de datos**: Firebase Firestore
- **Infraestructura**: Docker Compose

## Requisitos previos

- Docker y Docker Compose v2
- Git
- Credenciales Firebase (archivo `keys/firebase.json`)

## Levantar el entorno de desarrollo

```bash
# 1. Clonar el repositorio
git clone https://github.com/SojoC/nexo_ppeam.git
cd nexo_ppeam

# 2. Asegurar que existe keys/firebase.json con credenciales válidas
# (Si no tienes credenciales, crea un archivo placeholder)

# 3. Construir las imágenes
docker compose build

# 4. Levantar los servicios
docker compose up -d

# 5. Verificar estado
docker compose ps

# 6. Ver logs
docker compose logs -f
```

## URLs de acceso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API (Swagger)**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

## Estructura del proyecto

```
nexo_ppeam/
├── backend/
│   ├── app.py                 # FastAPI app principal
│   ├── Dockerfile             # Imagen Python para backend
│   ├── requirements.txt       # Dependencias Python
│   ├── config/
│   │   ├── firebase.py        # Configuración Firebase
│   │   └── settings.py        # Settings de la app
│   ├── models/                # Modelos de datos
│   ├── routes/                # Endpoints de la API
│   ├── repository/            # Lógica de acceso a datos
│   └── realtime/              # WebSockets
├── frontend/
│   ├── Dockerfile             # Build Vite + nginx
│   ├── package.json
│   ├── src/
│   └── public/
├── keys/
│   └── firebase.json          # Credenciales Firebase
└── docker-compose.yml         # Orquestación de servicios
```

## Comandos útiles

```bash
# Reconstruir sin caché
docker compose build --no-cache

# Reiniciar servicios
docker compose restart

# Ver logs de un servicio específico
docker compose logs -f api
docker compose logs -f frontend

# Detener y limpiar
docker compose down -v

# Ejecutar comando en contenedor
docker compose exec api bash
```

## Troubleshooting

### Backend no arranca / unhealthy

1. Revisar logs: `docker compose logs api`
2. Verificar que `keys/firebase.json` existe y está montado
3. Comprobar que PYTHONPATH está configurado correctamente
4. Validar que todos los imports usan rutas relativas sin prefijo `backend.`

### Frontend no carga

1. Verificar que el backend está healthy: `curl http://localhost:8000/health`
2. Revisar logs: `docker compose logs frontend`
3. Comprobar puerto 3000 disponible: `netstat -ano | findstr :3000`

### Errores de CORS

1. Verificar `backend/config/settings.py` incluye el origen del frontend
2. Por defecto incluye: `http://localhost:3000` y `http://localhost:5173`
3. Agregar más orígenes en variable de entorno `ALLOWED_ORIGINS`

### ModuleNotFoundError en imports

Los imports deben ser relativos al directorio `/app` dentro del contenedor:
- ❌ `from backend.config.settings import ...`
- ✅ `from config.settings import ...`

## Variables de entorno

Configurables en `docker-compose.yml`:

- `FIREBASE_CREDENTIALS`: Ruta al archivo de credenciales dentro del contenedor
- `ALLOWED_ORIGINS`: Orígenes permitidos para CORS (separados por coma)
- `SECRET_KEY`: Clave secreta para JWT
- `PYTHONPATH`: Path de módulos Python (default: `/app`)

## Desarrollo local (sin Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
export FIREBASE_CREDENTIALS=../keys/firebase.json
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

## Licencia

[Especificar licencia]
