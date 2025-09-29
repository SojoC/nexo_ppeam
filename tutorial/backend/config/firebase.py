# backend/config/firebase.py
# Configuración y conexión a Firebase Firestore


import firebase_admin
from firebase_admin import credentials, firestore
from backend.config.settings import get_settings
from functools import lru_cache

@lru_cache(maxsize=1)
def get_firestore_client():
    settings = get_settings()
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()

@lru_cache(maxsize=1)
def get_collection_ref():
    settings = get_settings()
    client = get_firestore_client()
    return client.collection(settings.FIRESTORE_COLLECTION)

