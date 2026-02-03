import asyncio
from unittest.mock import MagicMock, patch
import os
import sys

# 1. Mock Environment Variables BEFORE importing services.db
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy-key"
os.environ["GEMINI_API_KEY"] = "dummy-key"

# 2. Mock Supabase Client creation to avoid actual connection attempt
with (
    patch('services.db.create_client') as mock_create_client,
    patch('services.db.supabase') as mock_supabase_instance
):
    # Now we can import safely
    import services.db 
    
    # Configure the mock instance
    mock_response = MagicMock()
    mock_response.data = [{"item_name": "Tomato", "quantity": 20, "unit": "kg", "id": 1}]
    
    # Mock chain: supabase.table().select().eq()...execute()
    # It's easier to mock the module-level 'supabase' object directly if it was already imported,
    # but since we patched create_client, services.db.supabase might be the mock return value.
    # Let's verify how services.db init works. It runs create_client at module level.
    # So we need to patch it inside the module dictionary or force reload.
    pass

# Simplified Approach:
# Since services.db runs code on import, the easiest way is to just let it run with dummy ENV vars
# (which we set above). We just need to make sure the library doesn't actually try to connect 
# if 'create_client' is called. But Supabase client DOES validate URL format.
# So "https://example.supabase.co" is fine.

# Re-import to apply env vars if it was already imported (unlikely in this script but good practice)
if 'services.db' in sys.modules:
    del sys.modules['services.db']
import services.db

# 3. Apply Mocks to the functions used by Agent
services.db.add_inventory_log = MagicMock(return_value=150)

# Mock the select query for "Query" intent
# We need to mock the `supabase` object RESIDING in services.db
mock_db_client = MagicMock()
services.db.supabase = mock_db_client

# Setup return for query
# chain: table -> select -> eq -> eq -> execute -> response.data
mock_query_response = MagicMock()
mock_query_response.data = [{"item_name": "Tomato", "quantity": 20, "unit": "kg"}]
mock_db_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_query_response

from services.agent_manager import agent_router

async def run_simulation():
    print("--- Starting Simulation ---")
    tenant_id = "test-tenant-123"

    # Scenario 1: Update Inventory
    print("\n[Scenario 1] User says: 'Add 50kg Potato'")
    mock_gemini_output_update = {
        "intent": "UPDATE",
        "item_name": "Potato",
        "quantity": 50,
        "unit": "kg",
        "action": "IN"
    }
    result_update = await agent_router(tenant_id, mock_gemini_output_update)
    print(f"Result: {result_update}")
    
    # Verify DB call
    services.db.add_inventory_log.assert_called()

    # Scenario 2: Query Inventory
    print("\n[Scenario 2] User asks: 'How many tomatoes?'")
    mock_gemini_output_query = {
        "intent": "QUERY",
        "item_name": "Tomato"
    }
    result_query = await agent_router(tenant_id, mock_gemini_output_query)
    print(f"Result: {result_query}")


if __name__ == "__main__":
    asyncio.run(run_simulation())
