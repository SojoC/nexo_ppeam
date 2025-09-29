#Idea: modelos de datos (validación y forma del JSON).
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ProductoIn(BaseModel):
     nombre: str = Field(min_length=1, max_length=100)
     precio: float = Field(gt=0, description="Debe ser mayor que 0")
     stock: int = Field(ge=0, description="No puede ser negativo")
     descripcion: Optional[str] = Field(default=None, max_length=200)

class ProductoOut(BaseModel):
     id: str
     nombre: str
     precio: float
     stock: int
     descripcion: Optional[str] = None
     