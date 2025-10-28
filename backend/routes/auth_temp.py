# Versión temporal de auth.py sin Firebase para testing
from datetime import datetime, timedelta
from typing import Optional
import os
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from jose import jwt

router = APIRouter(tags=["auth"])

# Configuración temporal
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_DEV_ONLY")

def hash_password(password: str) -> str:
    """Hash simple para testing (NO usar en producción)"""
    return hashlib.sha256((password + "salt").encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password simple para testing"""
    return hash_password(plain_password) == hashed_password

# Base de datos temporal en memoria para testing
temp_users_db = {}

def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class RegisterResponse(BaseModel):
    id: str
    email: EmailStr
    display_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/auth/register", response_model=RegisterResponse)
def register_user(body: RegisterRequest):
    """Registro temporal sin Firebase"""
    if body.email.lower() in temp_users_db:
        raise HTTPException(status_code=409, detail="El email ya está registrado.")
    
    password_hash = hash_password(body.password)
    user_data = {
        "email": body.email.lower(),
        "display_name": body.display_name or "",
        "password_hash": password_hash,
        "provider": "password",
        "role": "user",
        "active": True,
        "created_at": datetime.utcnow(),
    }
    
    temp_users_db[body.email.lower()] = user_data
    
    return RegisterResponse(
        id=body.email.lower(),
        email=body.email,
        display_name=user_data["display_name"]
    )

@router.post("/auth/login", response_model=TokenResponse)
def login_user(body: LoginRequest):
    """Login temporal sin Firebase"""
    user_data = temp_users_db.get(body.email.lower())
    if not user_data:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    
    if not verify_password(body.password, user_data["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    
    token = create_access_token(subject=user_data["email"], expires_minutes=60)
    return TokenResponse(access_token=token)