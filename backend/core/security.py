# Módulo centralizado para manejo de seguridad (JWT, hashing, etc.)
# Este archivo concentra toda la lógica de seguridad para evitar duplicación

from datetime import datetime, timedelta
from typing import Optional
import os
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ==================== CONFIGURACIÓN ====================

# Algoritmo de firma JWT (recomendado HS256 para aplicaciones simples)
ALGORITHM = "HS256"

# Clave secreta desde variables de entorno (CRÍTICO en producción)
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_DEV_ONLY")

# Contexto para hashing de contraseñas (bcrypt es el estándar actual)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de seguridad para extraer tokens Bearer automáticamente
security = HTTPBearer()

# ==================== UTILIDADES DE PASSWORD ====================

def hash_password(password: str) -> str:
    """
    Genera hash seguro de una contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash bcrypt de la contraseña
        
    Note:
        Nunca almacenar contraseñas en texto plano. Siempre usar hash.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña ingresada por el usuario
        hashed_password: Hash almacenado en la base de datos
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)

# ==================== UTILIDADES JWT ====================

def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    """
    Crea un token JWT firmado con el subject (identificador del usuario).
    
    Args:
        subject: Identificador único del usuario (email, ID, etc.)
        expires_minutes: Tiempo de vida del token en minutos
        
    Returns:
        Token JWT firmado como string
        
    Example:
        token = create_access_token("user@example.com", expires_minutes=120)
    """
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> str:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token: Token JWT a validar
        
    Returns:
        Subject (identificador del usuario) del token
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: subject no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return subject
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ==================== DEPENDENCIAS FASTAPI ====================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependencia de FastAPI para obtener el usuario actual desde el token JWT.
    
    Args:
        credentials: Credenciales HTTP Bearer extraídas automáticamente
        
    Returns:
        Subject del usuario autenticado
        
    Usage:
        @router.get("/protected")
        def protected_route(current_user: str = Depends(get_current_user)):
            return {"user": current_user}
    """
    return decode_access_token(credentials.credentials)

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    Dependencia opcional que no falla si no hay token.
    Útil para endpoints que pueden funcionar con o sin autenticación.
    
    Returns:
        Subject del usuario si está autenticado, None si no hay token
    """
    if credentials is None:
        return None
    try:
        return decode_access_token(credentials.credentials)
    except HTTPException:
        return None