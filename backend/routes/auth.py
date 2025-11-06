# Este archivo define endpoints de AUTENTICACIÓN para Nexo_PPEAM.
# - /auth/register: registro con email/clave (hash bcrypt), guardado en Firestore.
# - /auth/login: login con email/clave, genera JWT firmado con SECRET_KEY.
# - /auth/google y /auth/facebook: stubs (por ahora devuelven 501).
# - /auth/sms/request y /auth/sms/verify: flujo OTP simulado (almacena código temporal).

from datetime import datetime, timedelta  # para manejar expiración del token
from typing import Optional               # para tipos opcionales
import os                                 # para leer variables de entorno (SECRET_KEY)
import firebase_admin                     # SDK admin de Firebase
from firebase_admin import credentials, firestore  # para conectar con Firestore
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr  # validación de email
from jose import jwt                      # para firmar/leer JWT
from passlib.context import CryptContext  # para hashear/verificar contraseñas

router = APIRouter(tags=["auth"])  # agrupamos rutas bajo etiqueta "auth"

# ===================== CONFIGURACIÓN DE CRIPTO Y JWT =====================

# Algoritmo de firma del JWT (simétrico HS256)
ALGORITHM = "HS256"

# SECRET_KEY debe estar definida en entorno (p. ej. docker-compose)
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_DEV_ONLY")

# Contexto de hash (bcrypt recomendado)
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    """
    Crea un JWT con 'sub' = subject (normalmente el email del usuario).
    - subject: identificador del usuario (email/ID)
    - expires_minutes: minutos hasta caducar
    Devuelve: token firmado (str)
    """
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ===================== INICIALIZACIÓN FIRESTORE =====================

def get_db():
    """
    Inicializa Firebase Admin 1 sola vez y retorna el cliente de Firestore.
    Lee la ruta del archivo de credenciales desde FIREBASE_CREDENTIALS.
    """
    cred_path = os.environ.get("FIREBASE_CREDENTIALS", "/app/keys/firebase.json")
    if not firebase_admin._apps:  # evita inicializar múltiples veces
        firebase_admin.initialize_app(credentials.Certificate(cred_path))
    return firestore.client()

# ===================== MODELOS DE ENTRADA/SALIDA =====================

class RegisterRequest(BaseModel):
    # email del usuario a registrar (obligatorio y formato válido)
    email: EmailStr
    # contraseña en texto plano (se hashea en el servidor)
    password: str
    # nombre visible (opcional)
    display_name: Optional[str] = None

class RegisterResponse(BaseModel):
    # identificador del documento/usuario en Firestore (usamos el email como ID)
    id: str
    # email registrado
    email: EmailStr
    # nombre visible
    display_name: Optional[str] = None

class LoginRequest(BaseModel):
    # credenciales para iniciar sesión
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    # token de acceso (JWT)
    access_token: str
    # tipo de token (convención OAuth2)
    token_type: str = "bearer"

class SmsRequest(BaseModel):
    # número de teléfono al cual enviar OTP
    phone: str

class SmsVerifyRequest(BaseModel):
    # número de teléfono
    phone: str
    # código OTP cuando el usuario lo recibe
    code: str

# ===================== ENDPOINTS =====================

@router.post("/auth/register", response_model=RegisterResponse)
def register_user(body: RegisterRequest):
    """
    Crea un usuario con email/clave.
    - Verifica unicidad del email.
    - Guarda password_hash (bcrypt) y metadatos en Firestore.
    """
    db = get_db()
    users = db.collection("auth_users")  # Colección separada para auth

    # 1) ¿Ya existe un documento con ese email como ID?
    #    Estrategia: usamos el email como ID del documento para simplificar búsquedas.
    doc_ref = users.document(body.email.lower())
    doc = doc_ref.get()
    if doc.exists:
        raise HTTPException(status_code=409, detail="El email ya está registrado.")

    # 2) Hashear la contraseña con bcrypt (nunca guardes password en texto)
    password_hash = pwd_ctx.hash(body.password)

    # 3) Construir documento usuario
    user_doc = {
        "email": body.email.lower(),
        "display_name": body.display_name or "",
        "password_hash": password_hash,
        "provider": "password",             # registro local
        "role": "user",                     # por defecto usuario
        "active": True,                     # habilitado
        "created_at": firestore.SERVER_TIMESTAMP,  # type: ignore[attr-defined]
    }

    # 4) Guardar en Firestore con ID = email
    doc_ref.set(user_doc)

    # 5) Responder sin exponer la contraseña
    return RegisterResponse(id=doc_ref.id, email=body.email, display_name=user_doc["display_name"])

@router.post("/auth/login", response_model=TokenResponse)
def login_user(body: LoginRequest):
    """
    Valida email/clave:
    - Busca el usuario por ID = email.
    - Verifica el hash con bcrypt.
    - Devuelve JWT si es correcto.
    """
    db = get_db()
    doc_ref = db.collection("auth_users").document(body.email.lower())
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    data = doc.to_dict() or {}
    # Si el usuario se registró con OAuth, no tendrá password_hash
    if "password_hash" not in data:
        raise HTTPException(status_code=400, detail="El usuario usa proveedor externo (Google/Facebook).")

    # Verificar contraseña
    if not pwd_ctx.verify(body.password, data["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    # Generar JWT con 'sub' = email
    token = create_access_token(subject=data["email"], expires_minutes=60)
    return TokenResponse(access_token=token)

@router.get("/auth/google")
def login_google_stub():
    """
    Stub para login con Google.
    En producción: implementar OAuth (Auth Code Flow) y mapear al usuario Firestore.
    """
    raise HTTPException(status_code=501, detail="OAuth Google aún no implementado (stub).")

@router.get("/auth/facebook")
def login_facebook_stub():
    """
    Stub para login con Facebook.
    """
    raise HTTPException(status_code=501, detail="OAuth Facebook aún no implementado (stub).")

@router.post("/auth/sms/request")
def sms_request_code(body: SmsRequest):
    """
    Simula envío de OTP por SMS:
    - Genera código '123456' fijo (mock) y lo guarda con expiración de 5 min.
    - En producción: integrar proveedor SMS (Twilio, etc.).
    """
    db = get_db()
    # Para demo, usamos una colección temporal
    db.collection("otp_temp").document(body.phone).set({
        "phone": body.phone,
        "code": "123456",                         # MOCK
        "expire_at": datetime.utcnow() + timedelta(minutes=5),
        "created_at": firestore.SERVER_TIMESTAMP,  # type: ignore[attr-defined]
    })
    return {"status": "ok", "message": "Código OTP enviado (mock: 123456)"}

@router.post("/auth/sms/verify", response_model=TokenResponse)
def sms_verify_code(body: SmsVerifyRequest):
    """
    Verifica código OTP (mock).
    - Si es correcto, genera JWT asociado al teléfono como 'sub'.
    - Si el usuario por teléfono no existe, se podría crear uno mínimo.
    """
    db = get_db()
    doc_ref = db.collection("otp_temp").document(body.phone)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=400, detail="No hay OTP pendiente para este teléfono.")

    data = doc.to_dict() or {}
    # Validación simple del código (mock)
    if body.code != data.get("code"):
        raise HTTPException(status_code=400, detail="Código inválido.")

    # TODO: validar expiración (omitido para simplificar)
    token = create_access_token(subject=body.phone, expires_minutes=60)
    return TokenResponse(access_token=token)