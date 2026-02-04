import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from services.agent_manager import agent_router

load_dotenv()

# Setup DB
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def run_e2e_test():
    print("=== STARTING E2E SCENARIO TEST ===")
    
    # 1. Get Tenant (Simulating Test User)
    phone_number = "+923004118298"
    response = supabase.table("tenants").select("*").eq("phone_number", phone_number).execute()
    
    tenant_id = None
    if response.data:
        tenant_id = response.data[0]['id']
        print(f"✅ Found Tenant: {tenant_id}")
    else:
        # Create if not exists
        print("Creating test tenant...")
        data = {"phone_number": phone_number, "business_name": "E2E Test Shop"}
        res = supabase.table("tenants").insert(data).execute()
        tenant_id = res.data[0]['id']
        print(f"✅ Created Tenant: {tenant_id}")

    # Clear previous inventory for test
    supabase.table("inventory").delete().eq("tenant_id", tenant_id).eq("item_name", "Tomato").execute()
    print("🧹 Cleared old Tomato inventory.")

    # STEP 1: ADD 50 KG TOMATO
    # Simulating Gemini Output
    print("\n--- STEP 1: STOCK IN (50kg Tomato) ---")
    intent_in = {
        "intent": "UPDATE",
        "item_name": "Tomato",
        "quantity": 50,
        "unit": "kg",
        "action": "IN"
    }
    result_in = await agent_router(tenant_id, intent_in)
    print(f"Result: {result_in}")
    
    # Verify Inventory
    inv = supabase.table("inventory").select("*").eq("tenant_id", tenant_id).eq("item_name", "Tomato").execute()
    qty_1 = inv.data[0]['quantity']
    print(f"🔍 Audit: Current Stock is {qty_1} kg. (Expected: 50)")

    # STEP 2: SELL 35 KG TO IMAM @ 200
    print("\n--- STEP 2: SALE (35kg to Imam) ---")
    intent_sale = {
        "intent": "SALE",
        "item_name": "Tomato",
        "quantity": 35,
        "unit": "kg", # User said "box" rate, but "kg" quantity. Logic uses unit for record.
        "buyer_name": "Imam",
        "rate": 200,
        "is_credit": True # Assuming credit/ledger sale
    }
    result_sale = await agent_router(tenant_id, intent_sale)
    print(f"Result: {result_sale}")

    # Verify Final State
    inv_final = supabase.table("inventory").select("*").eq("tenant_id", tenant_id).eq("item_name", "Tomato").execute()
    qty_final = inv_final.data[0]['quantity']
    print(f"🔍 Audit: Final Stock is {qty_final} kg. (Expected: 15)")
    
    # Verify Transaction
    audit_log = supabase.table("transactions").select("*").eq("tenant_id", tenant_id).order("created_at", desc=True).limit(1).execute()
    last_tx = audit_log.data[0]
    print(f"🧾 Ledger Record: SOLD {last_tx['quantity']} {last_tx['unit']} {last_tx['item_name']} to {last_tx['buyer_name']} for {last_tx['total_amount']}")
    
    if qty_final == 15 and float(last_tx['total_amount']) == 7000.0:
        print("\n🎉 E2E TEST PASSED SUCCESSFULLY!")
    else:
        print("\n❌ E2E TEST FAILED.")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
