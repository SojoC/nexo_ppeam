# Manejo centralizado de excepciones y errores
# Este módulo define excepciones personalizadas y handlers globales

import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

# ==================== LOGGER ====================

logger = logging.getLogger(__name__)

# ==================== EXCEPCIONES PERSONALIZADAS ====================

class NexoBaseException(Exception):
    """
    Excepción base para todas las excepciones personalizadas de Nexo_PPEAM.
    
    Provides:
    - Mensaje de error consistente
    - Código de estado HTTP
    - Detalles adicionales opcional
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(NexoBaseException):
    """Error de autenticación (credenciales inválidas, token expirado, etc.)"""
    
    def __init__(self, message: str = "Error de autenticación", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)

class AuthorizationError(NexoBaseException):
    """Error de autorización (permisos insuficientes)"""
    
    def __init__(self, message: str = "No tienes permisos para esta acción", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)

class NotFoundError(NexoBaseException):
    """Recurso no encontrado"""
    
    def __init__(self, resource: str = "Recurso", details: Optional[Dict] = None):
        message = f"{resource} no encontrado"
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)

class ConflictError(NexoBaseException):
    """Conflicto con el estado actual (ej: email duplicado)"""
    
    def __init__(self, message: str = "Conflicto con datos existentes", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)

class NexoValidationError(NexoBaseException):
    """Error de validación de datos"""
    
    def __init__(self, message: str = "Datos inválidos", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)

class DatabaseError(NexoBaseException):
    """Error relacionado con la base de datos"""
    
    def __init__(self, message: str = "Error de base de datos", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class ExternalServiceError(NexoBaseException):
    """Error en servicios externos (SMS, OAuth, etc.)"""
    
    def __init__(self, service: str, message: str = "Error en servicio externo", details: Optional[Dict] = None):
        full_message = f"{message}: {service}"
        super().__init__(full_message, status.HTTP_502_BAD_GATEWAY, details)

# ==================== HANDLERS DE EXCEPCIONES ====================

async def nexo_exception_handler(request: Request, exc: NexoBaseException) -> JSONResponse:
    """
    Handler para excepciones personalizadas de Nexo_PPEAM.
    
    Convierte nuestras excepciones personalizadas en respuestas JSON consistentes.
    """
    logger.error(f"NexoException: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "type": type(exc).__name__
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler para HTTPException estándar de FastAPI.
    
    Normaliza las respuestas para mantener consistencia en la API.
    """
    logger.warning(f"HTTPException: {exc.detail} (status: {exc.status_code})")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "details": {},
            "type": "HTTPException"
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler para errores de validación de Pydantic.
    
    Convierte errores de validación en mensajes más amigables para el usuario.
    """
    logger.warning(f"ValidationError: {exc.errors()}")
    
    # Extraer el primer error para mensaje principal
    first_error = exc.errors()[0] if exc.errors() else {}
    field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
    message = first_error.get("msg", "Error de validación")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": f"Error en campo '{field}': {message}",
            "details": {"validation_errors": exc.errors()},
            "type": "ValidationError"
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler para excepciones no manejadas.
    
    Captura cualquier excepción que no tenga un handler específico
    y la convierte en una respuesta JSON sin exponer detalles internos.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "details": {},
            "type": "InternalServerError"
        }
    )

# ==================== UTILIDADES ====================

def create_error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Crea una respuesta de error consistente.
    
    Args:
        message: Mensaje de error para el usuario
        status_code: Código de estado HTTP
        details: Información adicional (opcional)
        
    Returns:
        JSONResponse formateada según el estándar de la API
        
    Usage:
        return create_error_response("Usuario no encontrado", 404)
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "message": message,
            "details": details or {},
            "type": "CustomError"
        }
    )

def log_and_raise(
    exception_class: type,
    message: str,
    details: Optional[Dict] = None,
    log_level: str = "error"
) -> None:
    """
    Utility para logging y raising de excepciones en una sola línea.
    
    Args:
        exception_class: Clase de excepción a lanzar
        message: Mensaje de error
        details: Detalles adicionales
        log_level: Nivel de logging (debug, info, warning, error)
        
    Usage:
        log_and_raise(NotFoundError, "Usuario no encontrado", {"user_id": user_id})
    """
    getattr(logger, log_level)(message, extra={"details": details})
    raise exception_class(message, details)