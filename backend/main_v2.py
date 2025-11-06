# Aplicación FastAPI mejorada con arquitectura limpia
# Incorpora todos los módulos refactorizados y mejores prácticas

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core modules
from core.config import get_settings
from core.exceptions import (
    NexoBaseException,
    nexo_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from core.database import check_database_health

# Routers
from routes.auth_v2 import router as auth_router
from routes.users_v2 import router as users_router
# Legacy routers (temporal)
from routes.contacts_firebase import router as contacts_router
from routes.messages import router as messages_router
from routes.campaigns import router as campaigns_router
from routes.realtime import router as realtime_router

# ==================== CONFIGURACIÓN ====================

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger("nexo_ppeam")
settings = get_settings()

# ==================== LIFECYCLE EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja eventos de inicio y cierre de la aplicación.
    
    Startup:
    - Verifica conexión a base de datos
    - Inicializa servicios
    - Log de configuración
    
    Shutdown:
    - Limpieza de recursos
    - Log de cierre
    """
    # Startup
    logger.info("🚀 Iniciando Nexo_PPEAM API...")
    logger.info(f"📊 Configuración: {settings.app_name} v{settings.app_version}")
    logger.info(f"🌍 Ambiente: {'Desarrollo' if settings.debug else 'Producción'}")
    
    try:
        # Verificar conexión a base de datos
        db_health = check_database_health()
        if db_health["connected"]:
            logger.info("✅ Conexión a Firestore establecida")
        else:
            logger.error(f"❌ Error conectando a Firestore: {db_health['message']}")
            
        logger.info("🎯 API lista para recibir requests")
        
    except Exception as e:
        logger.error(f"💥 Error en startup: {str(e)}")
        raise
    
    yield  # Aquí la aplicación ejecuta
    
    # Shutdown
    logger.info("🛑 Cerrando Nexo_PPEAM API...")
    logger.info("👋 Aplicación cerrada correctamente")

# ==================== APLICACIÓN ====================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Nexo_PPEAM - API de Gestión

    Sistema integral para gestión de usuarios, autenticación y comunicaciones
    para la comunidad de Testigos de Jehová.

    ### Características principales:

    * 🔐 **Autenticación robusta** - JWT, OAuth, SMS OTP
    * 👥 **Gestión de usuarios** - CRUD completo con validaciones
    * 📱 **API moderna** - REST con documentación automática
    * 🏗️ **Arquitectura limpia** - Separación de responsabilidades
    * 🔍 **Búsquedas avanzadas** - Filtros y paginación
    * 📊 **Estadísticas** - Reportes y métricas

    ### Tecnologías:

    * FastAPI + Pydantic para validaciones
    * Firebase Firestore como base de datos
    * JWT para autenticación stateless
    * Docker para containerización

    ### Versiones API:

    * **v2** - Versión actual (recomendada)
    * **v1** - Legacy (temporal)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)

# ==================== MIDDLEWARE ====================

# CORS - Configuración robusta
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"]  # Para paginación
)

# Middleware personalizado para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware que registra todas las requests HTTP.
    
    Logs:
    - Método y URL
    - IP del cliente
    - User-Agent
    - Tiempo de respuesta
    - Status code
    """
    import time
    
    start_time = time.time()
    
    # Extraer información del request
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)
    user_agent = request.headers.get("User-Agent", "unknown")
    
    # Ejecutar request
    response = await call_next(request)
    
    # Calcular tiempo de respuesta
    process_time = time.time() - start_time
    
    # Log estructurado
    logger.info(
        f"{method} {url} - {response.status_code} - "
        f"{process_time:.3f}s - IP:{client_ip} - UA:{user_agent[:50]}..."
    )
    
    # Añadir headers de tiempo de respuesta
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# ==================== EXCEPTION HANDLERS ====================

# Registrar handlers personalizados
app.add_exception_handler(NexoBaseException, nexo_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, general_exception_handler)  # type: ignore[arg-type]

# Handlers FastAPI estándar
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]

# ==================== ROUTERS ====================

# Health check antes que otros routers
@app.get("/health", tags=["health"], summary="Health Check")
async def health_check():
    """
    Endpoint de health check para monitoring.
    
    Verifica:
    - Estado de la aplicación
    - Conexión a base de datos
    - Configuración básica
    
    Returns:
        Estado detallado del sistema
    """
    db_health = check_database_health()
    
    return {
        "status": "healthy" if db_health["connected"] else "unhealthy",
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug
        },
        "database": db_health,
        "timestamp": db_health["timestamp"]
    }

# API v2 (Nueva arquitectura)
app.include_router(auth_router, prefix="/api/v2")
app.include_router(users_router, prefix="/api/v2")

# Legacy API (Compatibilidad temporal)
app.include_router(contacts_router, prefix="/api/v1", tags=["v1-legacy"])
app.include_router(messages_router, prefix="/api/v1", tags=["v1-legacy"])
app.include_router(campaigns_router, prefix="/api/v1", tags=["v1-legacy"])
app.include_router(realtime_router, prefix="/api/v1", tags=["v1-legacy"])

# ==================== ROOT ENDPOINT ====================

@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raíz con información de la API.
    
    Returns:
        Información básica y enlaces útiles
    """
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "api_versions": {
            "v2": "/api/v2",
            "v1": "/api/v1 (legacy)"
        },
        "health": "/health",
        "status": "operational"
    }

# ==================== CONFIGURACIÓN ADICIONAL ====================

# Configurar tags metadata para la documentación
if not app.openapi_tags:
    app.openapi_tags = [
        {
            "name": "health",
            "description": "Health checks y monitoreo del sistema"
        },
        {
            "name": "auth",
            "description": "Autenticación y gestión de tokens JWT"
        },
        {
            "name": "users",
            "description": "Gestión de perfiles de usuarios (CRUD completo)"
        },
        {
            "name": "v1-legacy",
            "description": "Endpoints legacy (v1) - Usar v2 para nuevos desarrollos"
        }
    ]

# ==================== DESARROLLO ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🔧 Ejecutando en modo desarrollo")
    
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )