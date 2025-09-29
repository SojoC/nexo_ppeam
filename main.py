from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
from backend.config.config import get_settings   



app = FastAPI()
settings = get_settings()   

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/hola/{nombre1}")
def hola(nombre1: str):
    return {"mensaje": f"hola {nombre1}"}

@app.get("/hola/{nombre}")
def hola(nombre: str):
    return {"mensaje": f"Hola {nombre}"}

@app.get("/summary")
def suamar(a:int, b:int):
    return {"Resultado": a+b}

class Usuario(BaseModel):
    nombre: str = Field(min_length=1)
    edad: int = Field(ge=0, le=120)
    email: EmailStr


@app.post("/usuaios", status_code=201)
def crear_usuario(u: Usuario):
    return {"ok": True, "usuario": u}


class Producto(BaseModel):
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)

# Inicializar base de datos en memoria y el contador de IDs
db: Dict[int, Producto] = {}
auto_id = 0

@app.post("/productos", status_code=201)
def crear_producto(p:Producto):
    global auto_id
    auto_id += 1
    db[auto_id] = p
    return {"id": auto_id, "data": p}

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLWED_ORIGINS,  # Usar configuración desde settings
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)