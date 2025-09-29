# Nexo_PPEAM API

API REST para gestión de contactos usando FastAPI y Firestore.

## Endpoints principales

- `POST /contacts` — Crear contacto
- `GET /contacts` — Listar contactos
- `GET /contacts/{contact_id}` — Obtener contacto por ID
- `PATCH /contacts/{contact_id}` — Actualizar contacto
- `DELETE /contacts/{contact_id}` — Eliminar contacto

## Estructura de carpetas

Ver `estructura_carpetas.txt` para la estructura actualizada.

## Requisitos

Ver `backend/requirements.txt` para dependencias.

## Configuración

Variables en `.env`:
- `FIREBASE_CREDENTIALS`
- `FIRESTORE_COLLECTION`
- `ALLWED_ORIGINS`

## Ejemplo de uso

Consulta la documentación interactiva en `/docs`.
