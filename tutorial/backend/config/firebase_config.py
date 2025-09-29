import firebase_admin
from firebase_admin import credentials, firestore
import os
from .config import get_settings

print('Ejecutando')

def get_db():
    try:
        if not firebase_admin._apps:
            settings = get_settings()
            key_path = os.path.join(os.getcwd(), settings.FIREBASE_CREDENTIALS)
            if not key_path:
                raise FileNotFoundError("El archivo de credenciales de Firebase no se encontró.")
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
           
        
        return  firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise
