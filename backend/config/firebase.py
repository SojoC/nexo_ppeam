import os, pathlib
import firebase_admin
from firebase_admin import credentials, firestore
from .settings import get_settings

_db = None
#Convierte la ruta del archivo de credenciales en una ruta absoluta, asegurando que siempre se encuentre el archivo correcto.
def _resolve_key_path(raw: str) -> str:
    p = pathlib.Path(raw)
    return str(p if p.is_absolute() else (pathlib.Path(os.getcwd()) / raw).resolve())

def get_db():
    global _db
    if _db is not None:
        return _db

    s = get_settings()
    key_path = _resolve_key_path(s.FIREBASE_CREDENTIALS)
    if not os.path.exists(key_path):
        raise RuntimeError(f"FIREBASE_CREDENTIALS not found at: {key_path}")

    if not firebase_admin._apps:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db

def get_collection_ref():
    return get_db().collection(get_settings().FIRESTORE_COLLECTION)

def get_messages_collection_ref():
    return get_db().collection(get_settings().FIRESTORE_MESSAGES_COLLECTION)

def get_campaigns_collection_ref():
    from .settings import get_settings
    return get_db().collection(get_settings().FIRESTORE_CAMPAIGNS_COLLECTION)

