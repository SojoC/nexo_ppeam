#Idea: aquí van los endpoints (rutas) del CRUD usando APIRouter.
from fastapi import APIRouter, Depends, HTTPException,Header, status
from typing import List
from app.schemas import ProductoIn, ProductoOut
from app import store_firestore as store

router = APIRouter(tags=["productos"])

# -------- Dependencia simple (mini seguridad) --------

def require_token(x_token: str = Header(..., alias="X-Token")):
    if x_token != "secreto123":
        # 401 Unauthorized
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Token invalido o faltante")

    
#Rutas EndPoint

@router.get("/productos", response_model=List[ProductoOut])
def listar():
    return store.listar_productos()

@router.get("/productos/{pid}", response_model=ProductoOut)
def obtener(pid: str):
    producto = store.obtener_pruducto(pid)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("/productos", response_model=ProductoOut, status_code=201, dependencies=[Depends(require_token)])
def crear(producto: ProductoIn):
    return store.crear_producto(producto)

@router.put("/productos/{pid}", response_model=ProductoOut, dependencies=[Depends(require_token)])
def actualizar(pid: str, cambios: ProductoIn):
    producto = store.actualizar_producto(pid, cambios.model_dump())
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.delete("/productos/{pid}", response_model=dict, dependencies=[Depends(require_token)])
def borrar(pid: str):
    if not store.borrar_producto(pid):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"detail": "Producto eliminado"}
# Eliminar devuelve un dict con mensaje de éxito