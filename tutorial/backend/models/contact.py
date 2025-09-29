from pydantic import BaseModel, Field, AliasChoices, ConfigDict
from typing import Optional

# API canónica en minúsculas; aceptamos también las variantes de Firestore (Mayúsculas/espacios)

class ContactIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    nombre: str = Field(validation_alias=AliasChoices('nombre', 'Nombre', 'Nómbre'))
    circuito: str = Field(validation_alias=AliasChoices('circuito', 'Circuito'))
    telefono: str = Field(validation_alias=AliasChoices('telefono', 'Telefono', 'Teléfono'))

    congregacion: Optional[str] = Field(default=None, validation_alias=AliasChoices('congregacion', 'Congregacion', 'Congregación'))
    fecha_de_nacimiento: Optional[str] = Field(default=None, validation_alias=AliasChoices('fecha_de_nacimiento','Fecha_de_nacimiento','fechaNacimiento','Fecha_de_nacimiento','Fecha de nacimiento','fecha de nacimiento'))
    fecha_de_bautismo: Optional[str] = Field(default=None, validation_alias=AliasChoices('fecha_de_bautismo','Fecha_de_bautismo','fechaBautismo','Fecha_de_bautismo','Fecha de bautismo','fecha de bautismo'))
    privilegio: Optional[str] = Field(default=None, validation_alias=AliasChoices('privilegio','Privilegio','Privilegio'))
    direccion_de_habitacion: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices('direccion_de_habitacion','Direccion de habitacion','Dirección de habitación','Direccion','direccion')
    )
    id_externo: Optional[str | int] = Field(default=None, validation_alias=AliasChoices('id_externo','Id','id','ID','ID_externo','Id_externo'))

class ContactOut(ContactIn):
    id: str

class ContactUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    nombre: Optional[str] = Field(default=None, validation_alias=AliasChoices('nombre', 'Nombre', 'Nómbre'))
    circuito: Optional[str] = Field(default=None, validation_alias=AliasChoices('circuito', 'Circuito'))
    telefono: Optional[str] = Field(default=None, validation_alias=AliasChoices('telefono', 'Telefono', 'Teléfono'))
    congregacion: Optional[str] = Field(default=None, validation_alias=AliasChoices('congregacion', 'Congregacion', 'Congregación'))
    fecha_de_nacimiento: Optional[str] = Field(default=None, validation_alias=AliasChoices('fecha_de_nacimiento','Fecha_de_nacimiento','fechaNacimiento','Fecha_de_nacimiento','Fecha de nacimiento','fecha de nacimiento'))
    fecha_de_bautismo: Optional[str] = Field(default=None, validation_alias=AliasChoices('fecha_de_bautismo','Fecha_de_bautismo','fechaBautismo','Fecha_de_bautismo','Fecha de bautismo','fecha de bautismo'))
    privilegio: Optional[str] = Field(default=None, validation_alias=AliasChoices('privilegio','Privilegio','Privilegio'))
    direccion_de_habitacion: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices('direccion_de_habitacion','Direccion de habitacion','Dirección de habitación','Direccion','direccion')
    )
    id_externo: Optional[str | int] = Field(default=None, validation_alias=AliasChoices('id_externo','Id','id','ID','ID_externo','Id_externo'))
