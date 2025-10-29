"""
Router legacy que fue movido a `backend/legacy/routes/contacts_firebase.py`.

Se redefine `router` re-exportando el router real desde el paquete `legacy`
para mantener compatibilidad si algún módulo todavía importa
`routes.contacts_firebase`.
"""

from legacy.routes.contacts_firebase import router as router
