import asyncio
from services.db import add_inventory_log

# Mocking the DB interaction for demonstration if real DB isn't connected or we want a quick logic check
# But let's assume we are calling the real functions which we defined in db.py
# Note: This script assumes 'db.py' functions are working or we mock them.
# To be safe and show logic, we will implement a logic flow here.

def simulate_counting_logic():
    print("--- Simulating Digital Munshi 'Counting' ---")
    
    current_stock = 100
    print(f"Start: Stock is {current_stock} Bori.")
    
    # Transaction 1: Restock (IN)
    incoming = 50
    current_stock += incoming
    print(f"Action: Loaded {incoming} Bori. (IN)")
    print(f"Count: New Stock is {current_stock} Bori.")
    
    # Transaction 2: Sale (OUT)
    sale_qty = 10
    current_stock -= sale_qty
    print(f"Action: Sold {sale_qty} Bori to Rashid. (OUT)")
    print(f"Count: New Stock is {current_stock} Bori.")
    
    # Transaction 3: Sale (OUT)
    sale_qty_2 = 5
    current_stock -= sale_qty_2
    print(f"Action: Sold {sale_qty_2} Bori to Aslam. (OUT)")
    print(f"Count: New Stock is {current_stock} Bori.")
    
    return current_stock

if __name__ == "__main__":
    simulate_counting_logic()
