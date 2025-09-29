from typing import Dict, List, Optional
from app.schemas import ProductoIn, ProductoOut 
from app.firebase import get_db

COL= "productos"

db  =get_db()
def crear_producto(data: ProductoIn) -> ProductoOut:
    bd= get_db()
    doc_ref= bd.collection(COL).document()
    doc= data.model_dump() # el valor de la variable doc la convierte en un diccionario
    doc_ref.set(doc)
    return ProductoOut(id=doc_ref.id, **doc)

def obtener_pruducto(pid: str) -> Optional[ProductoOut]:
    bd= get_db()
    doc_ref= bd.collection(COL).document(pid)
    doc= doc_ref.get()
    if not doc.exists:
        return None
    return ProductoOut(id=doc.id, **doc.to_dict())

def listar_productos(limit: int=10) -> List[ProductoOut]:
    bd= get_db()
    docs= bd.collection(COL).limit(limit).stream()  
    
    return [ProductoOut(id=doc.id, **doc.to_dict()) for doc in docs] 

def actualizar_producto(pid: str, cambios: Dict) -> Optional[ProductoOut]:  
    ref=db.collection(COL).document(pid)
    if not ref.get().exists:
        return None
    ref.update(cambios)
    return ProductoOut(id=pid, **ref.get().to_dict())
  
def borrar_producto(pid: str) -> bool:
    ref=db.collection(COL).document(pid)
    if not ref.get().exists:
        return False
    ref.delete()
    return True  

def buscar_dsto (datos:str)->Optional[ProductoOut]:
    docs= db.collection(COL).where("nombre", "==", datos).stream()
    
    return ProductoOut(id=docs.id, **docs)

#