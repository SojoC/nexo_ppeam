from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from backend.models.contact import ContactIn, ContactOut, ContactUpdate
from backend.repository.contacts_repository import (
    create_contact, get_contact, list_contacts, update_contact, delete_contact
)

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("", response_model=ContactOut)
def create_contact_endpoint(body: ContactIn):
    created = create_contact(body.model_dump())
    return ContactOut(**created)

@router.get("", response_model=Dict[str, Any])
def list_contacts_endpoint(
    limit: int = Query(50, ge=1, le=200),
    circuito: Optional[str] = Query(None),
    order_by: str = Query("nombre"),
    page_token: Optional[str] = Query(None)
):
    items, next_token = list_contacts(limit=limit, circuito=circuito, order_by_canonical=order_by, page_token=page_token)
    return {"items": [ContactOut(**i) for i in items], "next_page_token": next_token}

@router.get("/{contact_id}", response_model=ContactOut)
def get_contact_endpoint(contact_id: str):
    item = get_contact(contact_id)
    if not item:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactOut(**item)

@router.patch("/{contact_id}", response_model=ContactOut)
def update_contact_endpoint(contact_id: str, body: ContactUpdate):
    updated = update_contact(contact_id, body.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactOut(**updated)

@router.delete("/{contact_id}", status_code=204)
def delete_contact_endpoint(contact_id: str):
    ok = delete_contact(contact_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Contact not found")
    return
