# Rutas de autenticación refactorizadas usando el AuthService
# Endpoints limpios que delegan la lógica al service layer

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from services.auth_service import get_auth_service, AuthService
from core.security import get_current_user, get_optional_current_user
from core.exceptions import NexoBaseException

# ==================== ROUTER ====================

router = APIRouter(tags=["auth"], prefix="/auth")

# ==================== MODELOS PYDANTIC ====================

class RegisterRequest(BaseModel):
    """Modelo para registro de usuario"""
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class RegisterResponse(BaseModel):
    """Respuesta de registro exitoso"""
    id: str
    email: str
    display_name: str
    provider: str
    role: str

class LoginRequest(BaseModel):
    """Modelo para login"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Respuesta con token JWT"""
    access_token: str
    token_type: str = "bearer"

class SmsRequest(BaseModel):
    """Modelo para solicitar OTP por SMS"""
    phone: str

class SmsVerifyRequest(BaseModel):
    """Modelo para verificar OTP por SMS"""
    phone: str
    code: str

class ChangePasswordRequest(BaseModel):
    """Modelo para cambio de contraseña"""
    current_password: str
    new_password: str

class UserInfoResponse(BaseModel):
    """Información del usuario autenticado"""
    id: str
    email: str
    display_name: str
    provider: str
    role: str
    active: bool

# ==================== ENDPOINTS ====================

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    body: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Registra un nuevo usuario con email y contraseña.
    
    - **email**: Dirección de email válida (será el identificador único)
    - **password**: Contraseña de al menos 6 caracteres
    - **display_name**: Nombre para mostrar (opcional)
    
    Returns:
        Datos del usuario registrado (sin contraseña)
        
    Raises:
        409: Si el email ya está registrado
        422: Si los datos son inválidos
    """
    result = await auth_service.register_user(
        email=body.email,
        password=body.password,
        display_name=body.display_name
    )
    
    return RegisterResponse(**result)

@router.post("/login", response_model=TokenResponse)
async def login_user(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Autentica un usuario y devuelve token JWT.
    
    - **email**: Email registrado
    - **password**: Contraseña del usuario
    
    Returns:
        Token de acceso JWT válido por 24 horas
        
    Raises:
        401: Si las credenciales son incorrectas
        400: Si el usuario usa otro proveedor (Google, Facebook)
    """
    result = await auth_service.login_user(
        email=body.email,
        password=body.password
    )
    
    return TokenResponse(**result)

@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: str = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Obtiene información del usuario autenticado.
    
    Requires:
        Token JWT válido en header Authorization: Bearer <token>
        
    Returns:
        Información del perfil del usuario autenticado
        
    Raises:
        401: Si el token es inválido o ha expirado
        404: Si el usuario no existe
    """
    user_info = await auth_service.get_user_by_token(current_user)
    
    if not user_info:
        raise NexoBaseException("Usuario no encontrado", status_code=404)
    
    return UserInfoResponse(**user_info)

@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: str = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Cambia la contraseña del usuario autenticado.
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 6 caracteres)
    
    Requires:
        Token JWT válido
        
    Returns:
        Confirmación del cambio
        
    Raises:
        401: Si la contraseña actual es incorrecta
        422: Si la nueva contraseña es inválida
    """
    await auth_service.change_password(
        email=current_user,
        current_password=body.current_password,
        new_password=body.new_password
    )
    
    return {"message": "Contraseña cambiada exitosamente"}

# ==================== SMS OTP ====================

@router.post("/sms/request")
async def request_sms_otp(
    body: SmsRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Solicita código OTP por SMS (versión mock).
    
    - **phone**: Número de teléfono (mínimo 10 dígitos)
    
    Returns:
        Confirmación del envío (en modo mock muestra el código)
        
    Note:
        En producción, el código se envía por SMS real y no se expone en la respuesta.
        
    Raises:
        422: Si el número de teléfono es inválido
        502: Si hay error con el proveedor SMS
    """
    result = await auth_service.request_sms_otp(body.phone)
    return result

@router.post("/sms/verify", response_model=TokenResponse)
async def verify_sms_otp(
    body: SmsVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verifica código OTP y retorna token JWT.
    
    - **phone**: Número de teléfono que recibió el OTP
    - **code**: Código de 6 dígitos recibido por SMS
    
    Returns:
        Token JWT válido (el subject será el número de teléfono)
        
    Raises:
        401: Si el código es incorrecto o ha expirado
        400: Si no hay OTP pendiente para ese teléfono
    """
    result = await auth_service.verify_sms_otp(
        phone=body.phone,
        code=body.code
    )
    
    return TokenResponse(**result)

# ==================== OAUTH STUBS ====================

@router.get("/google")
async def google_oauth_redirect(
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Stub para autenticación con Google OAuth.
    
    En producción este endpoint:
    1. Redirige al usuario a Google OAuth
    2. Recibe el callback con código de autorización
    3. Intercambia el código por token de acceso
    4. Obtiene información del usuario desde Google
    5. Crea/actualiza usuario en Firestore
    6. Retorna JWT propio
    
    Raises:
        501: Funcionalidad no implementada
    """
    await auth_service.google_oauth_callback("")

@router.get("/facebook")
async def facebook_oauth_redirect(
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Stub para autenticación con Facebook OAuth.
    
    Proceso similar al de Google OAuth.
    
    Raises:
        501: Funcionalidad no implementada
    """
    await auth_service.facebook_oauth_callback("")

# ==================== UTILIDADES ====================

@router.post("/refresh")
async def refresh_token(
    current_user: str = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Genera un nuevo token JWT para el usuario autenticado.
    
    Útil para renovar tokens próximos a expirar sin requerir login.
    
    Requires:
        Token JWT válido (aunque esté próximo a expirar)
        
    Returns:
        Nuevo token JWT con tiempo de vida completo
    """
    from core.security import create_access_token
    from core.config import get_settings
    
    settings = get_settings()
    new_token = create_access_token(
        subject=current_user,
        expires_minutes=settings.jwt_expire_minutes
    )
    
    return TokenResponse(access_token=new_token)

@router.post("/logout")
async def logout_user(
    current_user: str = Depends(get_current_user)
):
    """
    Endpoint de logout (principalmente para consistencia de API).
    
    Como usamos JWT stateless, el logout real debe hacerse en el cliente
    eliminando el token del almacenamiento local.
    
    Para logout forzado del lado servidor, se requeriría:
    - Lista negra de tokens (blacklist)
    - Store Redis/Memcached para tokens inválidos
    - Verificación en cada request
    
    Returns:
        Confirmación de logout
    """
    return {
        "message": "Logout exitoso",
        "note": "Elimina el token del almacenamiento local del cliente"
    }