from services.db import add_inventory_log, supabase

def update_inventory_tool(tenant_id: str, item_name: str, quantity: float, unit: str, action: str):
    """
    Updates the inventory count for a specific item.
    """
    new_qty = add_inventory_log(tenant_id, item_name, quantity, unit, action)
    return {"status": "success", "message": f"Updated {item_name}. New Quantity: {new_qty} {unit}"}

def query_inventory_tool(tenant_id: str, item_name: str):
    """
    Queries the current stock of an item.
    """
    response = supabase.table("inventory").select("*").eq("tenant_id", tenant_id).eq("item_name", item_name).execute()
    if response.data:
        item = response.data[0]
        return {"status": "success", "message": f"We have {item['quantity']} {item['unit']} of {item['item_name']}."}
    else:
        return {"status": "success", "message": f"No record found for {item_name}."}
