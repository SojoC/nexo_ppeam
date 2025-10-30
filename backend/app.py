import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from routes.contacts_firebase import router as contacts_router
from routes.messages import router as messages_router
from routes.campaigns import router as campaigns_router
from routes.realtime import router as realtime_router
from routes.auth_temp import router as auth_router
from routes.users_temp import router as users_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
logger = logging.getLogger("nexo_ppeam")

settings = get_settings()

# Normaliza ALLOWED_ORIGINS (acepta string separada por comas o lista)
origins = settings.ALLOWED_ORIGINS
if isinstance(origins, str):
    origins = [o.strip() for o in origins.split(",") if o.strip()]
    if not origins:
        origins = ["*"]

app = FastAPI(title="Nexo_PPEAM API (Firebase + FastAPI)")

# CORS configuración explícita para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],  # Explícito para desarrollo
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_check():
    logger.info("event=health_check status=ok")
    return {"status": "ok"}

app.include_router(contacts_router)
app.include_router(messages_router)
app.include_router(campaigns_router)
app.include_router(realtime_router)
app.include_router(auth_router)
app.include_router(users_router)

