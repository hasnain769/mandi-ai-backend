import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def get_tenant_by_phone(phone_number: str):
    response = supabase.table("tenants").select("*").eq("phone_number", phone_number).execute()
    if response.data:
        return response.data[0]
    return None

def add_inventory_log(tenant_id: str, item_name: str, quantity: float, unit: str, action: str):
    # This is a simplified logic. In a real app we might update a current stock table
    # and also keep a transaction log. For now, let's assume we update an inventory item.
    
    # First check if item exists
    response = supabase.table("inventory").select("*").eq("tenant_id", tenant_id).eq("item_name", item_name).execute()
    
    current_qty = 0
    if response.data:
        current_qty = response.data[0]['quantity']
        
    new_qty = current_qty
    if action.upper() == "IN":
        new_qty += quantity
    elif action.upper() == "OUT":
        new_qty -= quantity
        
    data = {
        "tenant_id": tenant_id,
        "item_name": item_name,
        "quantity": new_qty,
        "unit": unit
    }
    
    if response.data:
        # Update
        supabase.table("inventory").update(data).eq("id", response.data[0]['id']).execute()
    else:
        # Insert
        supabase.table("inventory").insert(data).execute()

    return new_qty

def record_transaction(tenant_id: str, item_name: str, quantity: float, unit: str, 
                      transaction_type: str, rate: float = None, buyer_name: str = None, 
                      is_credit: bool = False):
    """
    Records a transaction (Sale/Purchase) and updates inventory.
    """
    # 1. Update Inventory First (Reusing existing logic or refining it)
    action = "IN" if transaction_type == "PURCHASE" else "OUT"
    new_qty = add_inventory_log(tenant_id, item_name, quantity, unit, action)
    
    # 2. Calculate Total
    total_amount = 0
    if rate:
        total_amount = float(quantity) * float(rate)

    # 3. Insert Transaction Record
    try:
        data = {
            "tenant_id": tenant_id,
            "transaction_type": transaction_type,
            "item_name": item_name,
            "quantity": quantity,
            "unit": unit,
            "rate": rate,
            "total_amount": total_amount,
            "buyer_name": buyer_name,
            "is_credit": is_credit
        }
        supabase.table("transactions").insert(data).execute()
        return {"status": "success", "new_qty": new_qty, "total_amount": total_amount}
    except Exception as e:
        print(f"Error recording transaction: {e}")
        return {"status": "error", "message": str(e)}

def create_tenant(phone_number: str, business_name: str = "My Mandi Shop"):
    """
    Creates a new tenant in the database.
    """
    try:
        data = {
            "phone_number": phone_number,
            "business_name": business_name
        }
        response = supabase.table("tenants").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating tenant: {e}")
        return None

def get_inventory(tenant_id: str):
    """
    Fetches all inventory items for a specific tenant.
    """
    try:
        response = supabase.table("inventory").select("*").eq("tenant_id", tenant_id).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return []

def update_inventory_item(item_id: int, data: dict):
    """Updates an inventory item directly."""
    try:
        supabase.table("inventory").update(data).eq("id", item_id).execute()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_inventory_item(item_id: int):
    """Deletes an inventory item."""
    try:
        supabase.table("inventory").delete().eq("id", item_id).execute()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update_transaction(tx_id: str, data: dict):
    """Updates a transaction (e.g. correcting a rate/name)."""
    try:
        supabase.table("transactions").update(data).eq("id", tx_id).execute()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_transaction(tx_id: str):
    """Deletes a transaction record."""
    try:
        supabase.table("transactions").delete().eq("id", tx_id).execute()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
