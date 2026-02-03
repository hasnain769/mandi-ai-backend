from fastapi import APIRouter, HTTPException, Depends, Header
from services.db import get_tenant_by_phone, get_inventory
from typing import Optional

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
    return {"inventory": inventory, "user": user}
