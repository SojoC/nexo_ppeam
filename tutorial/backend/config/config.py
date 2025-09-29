from dotenv import load_dotenv
#from functools import lru_cache: Permite cachear funciones para que no se creen múltiples instancias de configuración.
from functools import lru_cache
import os
# 1 cargar variables de entorno desde un archivo .env
load_dotenv()

#carga el .env al entorno del proceso, os.getenv("NOMBRE", "fallback") → pide un valor del entorno; si no está, usa uno por defecto.
class Setting:
    def __init__(self) -> None:
        self.FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "datos_circuitos.json")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "sjmgrc-mtrmngs")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
        self.ALLWED_ORIGINS = os.getenv("ALLWED_ORIGINS", "https://localhost:5173,https://localhost:3000")
        raw = os.getenv("ALLWED_ORIGINS", "https://localhost:5173,https://localhost:3000")
        self.ALLWED_ORIGINS = [o.strip() for o in raw.split(",")] if raw != "*" else ["*"]

#@lru_cache → evita crear mil veces Settings(); es un singleton.

@lru_cache
def get_settings() -> Setting:
    return Setting()
