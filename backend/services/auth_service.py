# Servicio de autenticación - Lógica de negocio para auth
# Separa la lógica de autenticación de los endpoints para mejor testabilidad

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.cloud import firestore

from core.config import get_settings
from core.database import get_collection, create_document, get_document, update_document, delete_document
from core.security import hash_password, verify_password, create_access_token
from core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    NexoValidationError,
    ExternalServiceError
)

# ==================== LOGGER ====================

logger = logging.getLogger(__name__)

# ==================== MODELOS DE DATOS ====================

class UserAuthData:
    """Modelo para datos de autenticación de usuario"""
    
    def __init__(
        self,
        email: str,
        password_hash: Optional[str] = None,
        display_name: Optional[str] = None,
        provider: str = "password",
        role: str = "user",
        active: bool = True,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        self.email = email.lower()
        self.password_hash = password_hash
        self.display_name = display_name or ""
        self.provider = provider
        self.role = role
        self.active = active
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para Firestore"""
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "display_name": self.display_name,
            "provider": self.provider,
            "role": self.role,
            "active": self.active,
            "created_at": self.created_at,
            "last_login": self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserAuthData":
        """Crea instancia desde diccionario de Firestore"""
        return cls(
            email=data.get("email", ""),
            password_hash=data.get("password_hash"),
            display_name=data.get("display_name", ""),
            provider=data.get("provider", "password"),
            role=data.get("role", "user"),
            active=data.get("active", True),
            created_at=data.get("created_at"),
            last_login=data.get("last_login")
        )

# ==================== SERVICIO DE AUTENTICACIÓN ====================

class AuthService:
    """
    Servicio que maneja toda la lógica de autenticación.
    
    Responsibilities:
    - Registro de usuarios con validaciones
    - Login con múltiples proveedores
    - Gestión de tokens JWT
    - Validación de permisos
    - OTP por SMS (mock)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.auth_collection = get_collection(self.settings.auth_collection)
        self.otp_collection = get_collection(self.settings.otp_collection)
    
    # ==================== REGISTRO ====================
    
    async def register_user(
        self,
        email: str,
        password: str,
        display_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra un nuevo usuario con email y contraseña.
        
        Args:
            email: Email del usuario (será el ID del documento)
            password: Contraseña en texto plano
            display_name: Nombre para mostrar (opcional)
            
        Returns:
            Datos del usuario registrado (sin password_hash)
            
        Raises:
            ConflictError: Si el email ya existe
            NexoValidationError: Si los datos son inválidos
        """
        try:
            # Validar formato de email
            email = email.lower().strip()
            if not email or "@" not in email:
                raise NexoValidationError("Email inválido")
            
            # Validar contraseña
            if not password or len(password) < 6:
                raise NexoValidationError("La contraseña debe tener al menos 6 caracteres")
            
            # Verificar que el email no existe
            existing_user = get_document(self.settings.auth_collection, email)
            if existing_user:
                raise ConflictError("El email ya está registrado")
            
            # Crear usuario
            user_data = UserAuthData(
                email=email,
                password_hash=hash_password(password),
                display_name=display_name,
                provider="password"
            )
            
            # Guardar en Firestore usando email como ID
            create_document(self.settings.auth_collection, user_data.to_dict(), email)
            
            logger.info(f"Usuario registrado: {email}")
            
            # Retornar datos sin password_hash
            return {
                "id": email,
                "email": email,
                "display_name": user_data.display_name,
                "provider": user_data.provider,
                "role": user_data.role
            }
            
        except (ConflictError, NexoValidationError):
            raise
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            raise AuthenticationError(f"Error al registrar usuario: {str(e)}")
    
    # ==================== LOGIN ====================
    
    async def login_user(self, email: str, password: str) -> Dict[str, str]:
        """
        Autentica un usuario con email y contraseña.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Token de acceso JWT
            
        Raises:
            AuthenticationError: Si las credenciales son inválidas
        """
        try:
            email = email.lower().strip()
            
            # Buscar usuario
            user_data = get_document(self.settings.auth_collection, email)
            if not user_data:
                raise AuthenticationError("Credenciales inválidas")
            
            user = UserAuthData.from_dict(user_data)
            
            # Verificar que el usuario está activo
            if not user.active:
                raise AuthenticationError("Cuenta desactivada")
            
            # Verificar que usa autenticación por contraseña
            if user.provider != "password":
                raise AuthenticationError(
                    f"Este usuario usa autenticación {user.provider}. "
                    "Use el método correspondiente."
                )
            
            # Verificar contraseña
            if not user.password_hash or not verify_password(password, user.password_hash):
                raise AuthenticationError("Credenciales inválidas")
            
            # Actualizar último login
            update_document(
                self.settings.auth_collection,
                email,
                {"last_login": datetime.utcnow()}
            )
            
            # Generar token JWT
            access_token = create_access_token(
                subject=email,
                expires_minutes=self.settings.jwt_expire_minutes
            )
            
            logger.info(f"Login exitoso: {email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            raise AuthenticationError(f"Error al iniciar sesión: {str(e)}")
    
    # ==================== OTP SMS (MOCK) ====================
    
    async def request_sms_otp(self, phone: str) -> Dict[str, str]:
        """
        Solicita código OTP por SMS (versión mock).
        
        Args:
            phone: Número de teléfono
            
        Returns:
            Confirmación del envío
            
        Note:
            En producción, integrar con proveedor SMS real (Twilio, etc.)
        """
        try:
            # Validar formato básico de teléfono
            phone = phone.strip().replace(" ", "").replace("-", "")
            if len(phone) < 10:
                raise NexoValidationError("Número de teléfono inválido")
            
            # Generar código mock (en producción sería aleatorio)
            otp_code = "123456"
            expire_at = datetime.utcnow() + timedelta(minutes=5)
            
            # Guardar OTP temporal
            otp_data = {
                "phone": phone,
                "code": otp_code,
                "expire_at": expire_at,
                "attempts": 0,
                "created_at": datetime.utcnow()
            }
            
            create_document(self.settings.otp_collection, otp_data, phone)
            
            logger.info(f"OTP generado para {phone}: {otp_code}")
            
            # En producción: enviar SMS real
            if self.settings.sms_provider == "mock":
                return {
                    "status": "sent",
                    "message": f"Código OTP enviado (MOCK: {otp_code})",
                    "phone": phone
                }
            else:
                # TODO: Implementar envío real
                raise ExternalServiceError("SMS", "Proveedor SMS no configurado")
                
        except (NexoValidationError, ExternalServiceError):
            raise
        except Exception as e:
            logger.error(f"Error enviando OTP: {str(e)}")
            raise ExternalServiceError("SMS", f"Error al enviar OTP: {str(e)}")
    
    async def verify_sms_otp(self, phone: str, code: str) -> Dict[str, str]:
        """
        Verifica código OTP y retorna token JWT.
        
        Args:
            phone: Número de teléfono
            code: Código OTP ingresado
            
        Returns:
            Token de acceso JWT
            
        Raises:
            AuthenticationError: Si el código es inválido o expirado
        """
        try:
            phone = phone.strip().replace(" ", "").replace("-", "")
            
            # Buscar OTP
            otp_data = get_document(self.settings.otp_collection, phone)
            if not otp_data:
                raise AuthenticationError("No hay código OTP pendiente para este teléfono")
            
            # Verificar expiración
            expire_at = otp_data.get("expire_at")
            if expire_at and datetime.utcnow() > expire_at:
                # Limpiar OTP expirado
                delete_document(self.settings.otp_collection, phone)
                raise AuthenticationError("Código OTP expirado")
            
            # Verificar código
            if code != otp_data.get("code"):
                # Incrementar intentos
                attempts = otp_data.get("attempts", 0) + 1
                if attempts >= 3:
                    # Demasiados intentos, eliminar OTP
                    delete_document(self.settings.otp_collection, phone)
                    raise AuthenticationError("Demasiados intentos. Solicite un nuevo código.")
                else:
                    update_document(self.settings.otp_collection, phone, {"attempts": attempts})
                    raise AuthenticationError("Código inválido")
            
            # Código válido, limpiar OTP
            delete_document(self.settings.otp_collection, phone)
            
            # Generar token JWT (usando teléfono como subject)
            access_token = create_access_token(
                subject=phone,
                expires_minutes=self.settings.jwt_expire_minutes
            )
            
            logger.info(f"Login por SMS exitoso: {phone}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error verificando OTP: {str(e)}")
            raise AuthenticationError(f"Error al verificar código: {str(e)}")
    
    # ==================== OAUTH STUBS ====================
    
    async def google_oauth_callback(self, code: str) -> Dict[str, str]:
        """
        Stub para OAuth con Google.
        
        Args:
            code: Código de autorización de Google
            
        Returns:
            Token JWT (cuando se implemente)
            
        Raises:
            ExternalServiceError: Método no implementado
        """
        # TODO: Implementar OAuth con Google
        logger.warning("Intento de login con Google (no implementado)")
        raise ExternalServiceError("Google OAuth", "Autenticación con Google no implementada")
    
    async def facebook_oauth_callback(self, code: str) -> Dict[str, str]:
        """
        Stub para OAuth con Facebook.
        
        Args:
            code: Código de autorización de Facebook
            
        Returns:
            Token JWT (cuando se implemente)
            
        Raises:
            ExternalServiceError: Método no implementado
        """
        # TODO: Implementar OAuth con Facebook
        logger.warning("Intento de login con Facebook (no implementado)")
        raise ExternalServiceError("Facebook OAuth", "Autenticación con Facebook no implementada")
    
    # ==================== UTILIDADES ====================
    
    async def get_user_by_token(self, token_subject: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos del usuario desde el subject del token JWT.
        
        Args:
            token_subject: Subject del token (email o teléfono)
            
        Returns:
            Datos del usuario o None si no existe
        """
        try:
            # Primero intentar buscar por email
            user_data = get_document(self.settings.auth_collection, token_subject)
            if user_data:
                user = UserAuthData.from_dict(user_data)
                return {
                    "id": token_subject,
                    "email": user.email,
                    "display_name": user.display_name,
                    "provider": user.provider,
                    "role": user.role,
                    "active": user.active
                }
            
            # Si no se encuentra por email, podría ser un teléfono (login SMS)
            # TODO: Implementar búsqueda por teléfono si se necesita
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por token: {str(e)}")
            return None
    
    async def change_password(
        self,
        email: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            email: Email del usuario
            current_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            True si se cambió exitosamente
            
        Raises:
            AuthenticationError: Si la contraseña actual es incorrecta
            NexoValidationError: Si la nueva contraseña es inválida
        """
        try:
            # Validar nueva contraseña
            if not new_password or len(new_password) < 6:
                raise NexoValidationError("La nueva contraseña debe tener al menos 6 caracteres")
            
            # Verificar contraseña actual
            user_data = get_document(self.settings.auth_collection, email.lower())
            if not user_data:
                raise AuthenticationError("Usuario no encontrado")
            
            user = UserAuthData.from_dict(user_data)
            
            if not user.password_hash or not verify_password(current_password, user.password_hash):
                raise AuthenticationError("Contraseña actual incorrecta")
            
            # Actualizar contraseña
            new_hash = hash_password(new_password)
            update_document(
                self.settings.auth_collection,
                email.lower(),
                {"password_hash": new_hash}
            )
            
            logger.info(f"Contraseña cambiada para: {email}")
            return True
            
        except (AuthenticationError, NexoValidationError):
            raise
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {str(e)}")
            raise AuthenticationError(f"Error al cambiar contraseña: {str(e)}")

# ==================== SINGLETON ====================

_auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """
    Factory function que retorna instancia singleton del AuthService.
    
    Returns:
        Instancia de AuthService
        
    Usage:
        from services.auth_service import get_auth_service
        
        auth_service = get_auth_service()
        result = await auth_service.login_user(email, password)
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service