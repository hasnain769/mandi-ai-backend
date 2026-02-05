from fastapi import APIRouter, HTTPException, Depends, Header
from services.db import (
    get_tenant_by_phone, get_inventory, supabase, 
    update_inventory_item, delete_inventory_item, 
    update_transaction, delete_transaction
)
from typing import Optional, Any
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["api"])

# Dependency to get user from phone number header (Simple Auth for MVP)
# In production, this should verify a Firebase ID Token.
async def get_current_user(x_phone_number: Optional[str] = Header(None)):
    if not x_phone_number:
        raise HTTPException(status_code=401, detail="Missing X-Phone-Number header")
    
    tenant = get_tenant_by_phone(x_phone_number)
    if not tenant:
         raise HTTPException(status_code=401, detail="User not found")
    return tenant

@router.get("/dashboard")
async def get_dashboard_data(user: dict = Depends(get_current_user)):
    inventory = get_inventory(user['id'])
    
    # Fetch recent transactions
    transactions = []
    try:
        response = supabase.table("transactions").select("*").eq("tenant_id", user['id']).order("created_at", desc=True).limit(20).execute()
        transactions = response.data
    except Exception as e:
        print(f"Error fetching transactions: {e}")

    return {"inventory": inventory, "transactions": transactions, "user": user}

# --- Inventory CRUD ---
@router.put("/inventory/{item_id}")
async def update_inventory(item_id: int, payload: dict, user: dict = Depends(get_current_user)):
    return update_inventory_item(item_id, payload)

@router.delete("/inventory/{item_id}")
async def delete_inventory(item_id: int, user: dict = Depends(get_current_user)):
    return delete_inventory_item(item_id)

# --- Transaction CRUD ---
@router.put("/transactions/{tx_id}")
async def update_tx(tx_id: str, payload: dict, user: dict = Depends(get_current_user)):
    return update_transaction(tx_id, payload)

@router.delete("/transactions/{tx_id}")
async def delete_tx(tx_id: str, user: dict = Depends(get_current_user)):
    return delete_transaction(tx_id)
