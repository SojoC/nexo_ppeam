# Configuración centralizada de la aplicación
# Este archivo maneja todas las configuraciones y variables de entorno

import os
from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    
    Las variables se cargan desde:
    1. Variables de entorno del sistema
    2. Archivo .env (si existe)
    3. Valores por defecto definidos aquí
    
    Benefits:
    - Validación automática de tipos
    - Documentación clara de configuración requerida
    - Fácil testing con configuraciones diferentes
    """
    
    # ==================== APLICACIÓN ====================
    app_name: str = "Nexo_PPEAM API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # ==================== SERVIDOR ====================
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False  # Hot reload en desarrollo
    
    # ==================== SEGURIDAD ====================
    secret_key: str = "CHANGE_ME_DEV_ONLY"  # CRÍTICO: cambiar en producción
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 horas por defecto
    
    # ==================== CORS ====================
    # Orígenes permitidos para CORS (separados por comas en env)
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # ==================== BASE DE DATOS ====================
    # Firebase
    firebase_credentials: Optional[str] = None  # Path al archivo JSON
    firestore_project_id: Optional[str] = None
    
    # Collections names
    users_collection: str = "users"
    auth_collection: str = "auth_users"  
    otp_collection: str = "otp_temp"
    
    # ==================== EXTERNOS ====================
    # SMS Provider (para OTP)
    sms_provider: str = "mock"  # mock | twilio | etc
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # OAuth Providers
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    facebook_app_id: Optional[str] = None
    facebook_app_secret: Optional[str] = None
    
    # ==================== LOGGING ====================
    log_level: str = "INFO"
    log_format: str = "%(asctime)s %(levelname)s %(name)s :: %(message)s"
    
    # ==================== PAGINACIÓN ====================
    default_page_size: int = 50
    max_page_size: int = 200
    
    class Config:
        # Archivo de variables de entorno (opcional)
        env_file = ".env"
        # Prefijo para variables de entorno (ej: NEXO_SECRET_KEY)
        env_prefix = ""
        # Case sensitive para nombres de variables
        case_sensitive = False

# ==================== FACTORY FUNCTIONS ====================

@lru_cache()
def get_settings() -> Settings:
    """
    Factory function que devuelve una instancia singleton de Settings.
    
    El decorador @lru_cache asegura que solo se cree una instancia
    durante la vida de la aplicación, mejorando performance.
    
    Returns:
        Instancia configurada de Settings
        
    Usage:
        from core.config import get_settings
        settings = get_settings()
        print(settings.app_name)
    """
    return Settings()

def get_firebase_credentials_path() -> str:
    """
    Obtiene la ruta completa al archivo de credenciales de Firebase.
    
    Returns:
        Path absoluto al archivo de credenciales
        
    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    settings = get_settings()
    
    # Intentar varias ubicaciones comunes
    possible_paths = [
        settings.firebase_credentials,
        "/app/keys/firebase.json",  # Docker
        "./keys/firebase.json",     # Local
        os.getenv("FIREBASE_CREDENTIALS"),
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    raise FileNotFoundError(
        "No se encontró el archivo de credenciales de Firebase. "
        "Configura FIREBASE_CREDENTIALS o coloca el archivo en ./keys/firebase.json"
    )

def is_development() -> bool:
    """
    Determina si la aplicación está ejecutándose en modo desarrollo.
    
    Returns:
        True si está en desarrollo, False en producción
    """
    return get_settings().debug or os.getenv("ENVIRONMENT", "development") == "development"

def is_testing() -> bool:
    """
    Determina si la aplicación está ejecutándose en tests.
    
    Returns:
        True si está en modo test
    """
    return os.getenv("TESTING", "false").lower() == "true"