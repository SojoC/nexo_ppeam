#Idea: “base de datos” en memoria con funciones CRUD.
from typing import Dict, List, Optional
from app.schemas import ProductoIn, ProductoOut


# Diccionario: id -> ProductoOut
_DB: Dict[int, ProductoOut]= {}
_AUTO_ID=0

def _siguiente_id() -> int:
    global _AUTO_ID
    _AUTO_ID += 1
    return _AUTO_ID

def crear_producto(data: ProductoIn) -> ProductoOut:
    nuevo= ProductoOut(id=_siguiente_id(), **data.model_dump())
    _DB[nuevo.id]= nuevo
    return nuevo

def obtener_producto(pid : int) -> Optional [ProductoOut]: 
    return _DB.get(pid)

def listar_productos() -> List[ProductoOut]:
    return list(_DB.values())

def actualizar_producto(pid: int, data: ProductoIn) -> Optional[ProductoOut]:
    if pid not in _DB:
        return None
    actualizado = ProductoOut(id=pid, **data.model_dump())
    _DB[pid] = actualizado
    return actualizado

def borrar_producto(pid: int) -> bool:
    return _DB.pop(pid, None) is not None