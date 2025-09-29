import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import get_settings
from backend.routes.contacts_firebase import router as contacts_router
from backend.routes.messages import router as messages_router
from backend.routes.campaigns import router as campaigns_router
from backend.routes.realtime import router as realtime_router

# Logs básicos + formato legible
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
logger = logging.getLogger("nexo_ppeam")

settings = get_settings()

app = FastAPI(title="Nexo_PPEAM API (Firebase + FastAPI)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    logger.info("event=health_check status=ok")
    return {"status": "ok"}

app.include_router(contacts_router)
app.include_router(messages_router)

app.include_router(campaigns_router)


app.include_router(realtime_router)

