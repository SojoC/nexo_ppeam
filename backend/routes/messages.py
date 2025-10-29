"""
Router legacy movido a `backend/legacy/routes/messages.py`.

Re-export del router desde el paquete `legacy` para compatibilidad.
"""

from legacy.routes.messages import router as router
