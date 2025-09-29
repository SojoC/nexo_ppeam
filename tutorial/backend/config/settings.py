import os
from dataclasses import dataclass
from typing import List

@dataclass
class Settings:
    FIREBASE_CREDENTIALS: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALLOWED_ORIGINS: List[str]
    FIRESTORE_COLLECTION: str

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
        FIRESTORE_COLLECTION=os.getenv("FIRESTORE_COLLECTION", "contacts"),
    )
