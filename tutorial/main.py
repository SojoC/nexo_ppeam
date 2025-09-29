from fastapi import FastAPI
from app.routers.productos import router as productos_router
app=FastAPI("Tutorial API + Firebase", version="0.2.0")

@app.get("/")
def raiz():
    return  {"ok": True, "mensaje": "Hola FastAPI + Firebase"}

app.include_router(productos_router, prefix="/api")