import asyncio
from services.agent_manager import agent_router
from unittest.mock import patch, MagicMock

async def test_sale_routing():
    print("--- Testing Agent Router for SALE Intent ---")
    
    # Mock Data extracted from Gemini
    extraction_data = {
        "intent": "SALE",
        "item_name": "Potato",
        "quantity": 10,
        "unit": "Bori",
        "rate": 5000,
        "buyer_name": "Rashid Bhai",
        "is_credit": True
    }
    
    tenant_id = "test-tenant-id"
    
    # Mock DB function
    with patch("services.agent_manager.record_transaction") as mock_record:
        mock_record.return_value = {"status": "success", "new_qty": 40, "total_amount": 50000}
        
        result = await agent_router(tenant_id, extraction_data)
        
        print(f"Result: {result}")
        
        # Verify call
        mock_record.assert_called_once_with(
            tenant_id, "Potato", 10, "Bori", "SALE", 5000, "Rashid Bhai", True
        )
        print("SUCCESS: Router correctly called record_transaction with Sale details.")

if __name__ == "__main__":
    asyncio.run(test_sale_routing())
