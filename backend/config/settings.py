import os
import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Settings:
    FIREBASE_CREDENTIALS: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALLOWED_ORIGINS: List[str]
    FIRESTORE_COLLECTION: str
    FIRESTORE_MESSAGES_COLLECTION: str
    FIRESTORE_FIELD_MAP_JSON: str
    PHONE_DEFAULT_REGION: str  # NUEVO (para E.164, p.ej. "VE" o "US")
    FIRESTORE_CAMPAIGNS_COLLECTION: str  # NUEVO


def get_settings() -> Settings:
    
    
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except Exception:
        pass

    raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
    origins = [o.strip() for o in raw_origins.split(",")] if raw_origins != "*" else ["*"]

    return Settings(
        FIREBASE_CREDENTIALS=os.getenv("FIREBASE_CREDENTIALS", "keys/firebaseKey.json"),
        SECRET_KEY=os.getenv("SECRET_KEY", "sjmgrc-mtrmngs"),
        ALGORITHM=os.getenv("ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        ALLOWED_ORIGINS=origins,
        FIRESTORE_COLLECTION=os.getenv("FIRESTORE_COLLECTION", "Congregacion"),
        FIRESTORE_MESSAGES_COLLECTION=os.getenv("FIRESTORE_MESSAGES_COLLECTION", "Mensajes"),
        FIRESTORE_FIELD_MAP_JSON=os.getenv("FIRESTORE_FIELD_MAP_JSON", ""),
        PHONE_DEFAULT_REGION=os.getenv("PHONE_DEFAULT_REGION", "VE"),
        FIRESTORE_CAMPAIGNS_COLLECTION=os.getenv("FIRESTORE_CAMPAIGNS_COLLECTION", "Campanas"),

    )

def get_field_map() -> Dict[str, str]:
    default_map = {
        "nombre": "Nombre",
        "circuito": "Circuito",
        "telefono": "Telefono",
        "congregacion": "Congregacion",
        "fecha_de_nacimiento": "Fecha_de_nacimiento",
        "fecha_de_bautismo": "Fecha_de_bautismo",
        "privilegio": "Privilegio",
        "direccion_de_habitacion": "Direccion de habitacion",
        "id_externo": "Id",
    }
    s = get_settings()
    if not s.FIRESTORE_FIELD_MAP_JSON:
        return default_map
    try:
        overrides = json.loads(s.FIRESTORE_FIELD_MAP_JSON)
        if isinstance(overrides, dict):
            for k, v in overrides.items():
                if isinstance(k, str) and isinstance(v, str):
                    default_map[k] = v
    except Exception:
        pass
    return default_map
