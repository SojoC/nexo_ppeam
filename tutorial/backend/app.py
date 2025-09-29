from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import get_settings
from backend.routes.contacts import router as contacts_router

settings = get_settings()
app = FastAPI(title="Nexo_PPEAM API (Firebase + FastAPI)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(contacts_router)
