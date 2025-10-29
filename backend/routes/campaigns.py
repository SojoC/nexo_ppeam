"""
Router legacy movido a `backend/legacy/routes/campaigns.py`.

Re-export del router desde el paquete `legacy` para compatibilidad.
"""

from legacy.routes.campaigns import router as router
