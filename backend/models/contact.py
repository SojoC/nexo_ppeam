from pydantic import BaseModel, Field, AliasChoices, ConfigDict, model_validator, field_validator
from typing import Optional, Union, Any, Dict
import os, unicodedata

# ======================
# Helpers de normalización
# ======================

def _strip_accents(s: str) -> str:
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(ch for ch in nfkd if not unicodedata.combining(ch))

def _norm_key(k: str) -> str:
    k = k.strip()
    k = _strip_accents(k)
    k = k.replace(' ', '_')
    return k.lower()

# OJO: este mapping se usa SOLO en entradas (In/Update),
# no en salidas (Out) para no tocar el 'id' del documento.
_NORMALIZED_TO_CANONICAL = {
    "nombre": "nombre",
    "circuito": "circuito",
    "telefono": "telefono",
    "congregacion": "congregacion",
    "fecha_de_nacimiento": "fecha_de_nacimiento",
    "fecha_de_bautismo": "fecha_de_bautismo",
    "privilegio": "privilegio",
    "direccion_de_habitacion": "direccion_de_habitacion",
    # aceptar 'id' en la entrada como alias de id_externo
    "id": "id_externo",
    "id_externo": "id_externo",
}

def _to_e164(raw: str) -> str:
    import phonenumbers
    region = os.getenv("PHONE_DEFAULT_REGION", "VE")
    try:
        num = phonenumbers.parse(raw, region)
        if not phonenumbers.is_valid_number(num):
            raise ValueError("invalid phone")
        return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        # No rompemos la creación si el número es raro; lo dejamos como llegó
        return raw

# ======================
# MODELOS
# ======================

# Base "plana" sin normalizador: la usaremos como Out para no tocar 'id'
class _ContactBase(BaseModel):
    model_config = ConfigDict(extra='ignore')
    nombre: str
    circuito: str
    telefono: str
    congregacion: Optional[str] = None
    fecha_de_nacimiento: Optional[str] = None
    fecha_de_bautismo: Optional[str] = None
    privilegio: Optional[str] = None
    direccion_de_habitacion: Optional[str] = None
    id_externo: Optional[Union[str, int]] = None

# ---------- Entradas (con normalización + alias + E.164) ----------
class ContactIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    @model_validator(mode='before')
    @classmethod
    def _normalize_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            normalized: Dict[str, Any] = {}
            for k, v in data.items():
                NK = _norm_key(k)
                CK = _NORMALIZED_TO_CANONICAL.get(NK, k)
                normalized[CK] = v
            return normalized
        return data

    nombre: str = Field(min_length=1, max_length=120, validation_alias=AliasChoices('nombre', 'Nombre'))
    circuito: str = Field(min_length=1, max_length=120, validation_alias=AliasChoices('circuito', 'Circuito'))
    telefono: str = Field(min_length=3, max_length=30, validation_alias=AliasChoices('telefono', 'Telefono', 'Teléfono', 'teléfono'))
    congregacion: Optional[str] = Field(default=None, validation_alias=AliasChoices('congregacion', 'Congregacion'))
    fecha_de_nacimiento: Optional[str] = Field(default=None, validation_alias=AliasChoices('fecha_de_nacimiento','Fecha_de_nacimiento','fechaNacimiento'))
    fecha_de_bautismo: Optional[str] = Field(default=None, validation_alias=AliasChoices('fecha_de_bautismo','Fecha_de_bautismo','fechaBautismo'))
    privilegio: Optional[str] = Field(default=None, validation_alias=AliasChoices('privilegio','Privilegio'))
    direccion_de_habitacion: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices('direccion_de_habitacion','Direccion de habitacion','Dirección de habitación','Direccion','direccion')
    )
    id_externo: Optional[Union[str, int]] = Field(default=None, validation_alias=AliasChoices('id_externo','Id','id'))

    @field_validator("telefono")
    @classmethod
    def _norm_phone(cls, v: str) -> str:
        return _to_e164(v)

class ContactUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    @model_validator(mode='before')
    @classmethod
    def _normalize_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            normalized: Dict[str, Any] = {}
            for k, v in data.items():
                NK = _norm_key(k)
                CK = _NORMALIZED_TO_CANONICAL.get(NK, k)
                normalized[CK] = v
            return normalized
        return data

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=120, validation_alias=AliasChoices('nombre', 'Nombre'))
    circuito: Optional[str] = Field(default=None, min_length=1, max_length=120, validation_alias=AliasChoices('circuito', 'Circuito'))
    telefono: Optional[str] = Field(default=None, min_length=3, max_length=30, validation_alias=AliasChoices('telefono', 'Telefono', 'Teléfono', 'teléfono'))
    congregacion: Optional[str] = Field(default=None, validation_alias=AliasChoices('congregacion', 'Congregacion'))
    fecha_de_nacimiento: Optional[str] = Field(default=None, validation_alias=AliasChoices('fecha_de_nacimiento','Fecha_de_nacimiento','fechaNacimiento'))
    fecha_de_bautismo: Optional[str] = Field(default=None, validation_alias=AliasChoices('fecha_de_bautismo','Fecha_de_bautismo','fechaBautismo'))
    privilegio: Optional[str] = Field(default=None, validation_alias=AliasChoices('privilegio','Privilegio'))
    direccion_de_habitacion: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices('direccion_de_habitacion','Direccion de habitacion','Dirección de habitación','Direccion','direccion')
    )
    id_externo: Optional[Union[str, int]] = Field(default=None, validation_alias=AliasChoices('id_externo','Id','id'))

    @field_validator("telefono")
    @classmethod
    def _norm_phone(cls, v: str) -> str:
        return _to_e164(v)

# ---------- Salida (sin normalizador: NO tocar 'id') ----------
class ContactOut(_ContactBase):
    id: str
