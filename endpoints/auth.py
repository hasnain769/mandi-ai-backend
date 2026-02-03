from fastapi import APIRouter, HTTPException, Body
from services.db import get_tenant_by_phone, create_tenant
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    phone_number: str

class RegisterRequest(BaseModel):
    phone_number: str
    business_name: str = "My Mandi Shop"

@router.post("/login")
async def login(data: LoginRequest = Body(...)):
    # Standardize phone number format if needed (e.g. ensure + prefix)
    tenant = get_tenant_by_phone(data.phone_number)
    
    if not tenant:
        # In a real app we might return 404, but for security sometimes 200 with specific status is used.
        # Here we want the frontend to know they need to register.
        return {"status": "not_found", "message": "User not registered"}
    
    return {"status": "success", "user": tenant}

@router.post("/register")
async def register(data: RegisterRequest = Body(...)):
    # Check if already exists
    existing = get_tenant_by_phone(data.phone_number)
    if existing:
         return {"status": "success", "user": existing, "message": "User already exists"}

    new_tenant = create_tenant(data.phone_number, data.business_name)
    if not new_tenant:
        raise HTTPException(status_code=500, detail="Failed to create user")
        
    return {"status": "success", "user": new_tenant}
