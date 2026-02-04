import logging
# from google.adk.core import Agent, Model
from services.agent_tools import update_inventory_tool, query_inventory_tool
from services.db import record_transaction

# Setup simple logging
logging.basicConfig(level=logging.INFO)

# For this MVP, we are using the "JSON Intent" from Gemini as the implementation of the "Agent".
# The "Google ADK" part here is demonstrating how we would structure it if we had a text-chat interface.
# Since we are processing Voice-to-JSON directly, the "Routing" is effectively done by the JSON content.
# However, to strictly follow the requirement of "Agentic Logic", we will create a dispatcher function 
# that acts as the "Agent Router" based on the extracted intent.

async def agent_router(tenant_id: str, extraction_data: dict):
    """
    Routes the extracted intent to the correct tool/action.
    This acts as the deterministic 'Router Agent'.
    """
    intent = extraction_data.get("intent")
    
    if intent == "UPDATE":
        return update_inventory_tool(
            tenant_id,
            extraction_data.get("item_name"),
            extraction_data.get("quantity"),
            extraction_data.get("unit"),
            extraction_data.get("action")
        )
    
    elif intent == "SALE":
        return record_transaction(
            tenant_id,
            extraction_data.get("item_name"),
            extraction_data.get("quantity"),
            extraction_data.get("unit"),
            "SALE",
            extraction_data.get("rate"),
            extraction_data.get("buyer_name"),
            extraction_data.get("is_credit")
        )
    
    elif intent == "QUERY":
        return query_inventory_tool(
            tenant_id,
            extraction_data.get("item_name")
        )
        
    else:
        return {"status": "error", "message": "Unknown intent"}

# Note: A full ADK implementation would involve creating `Agent` classes with `tools` 
# and passing the text prompt to them. Since we are doing Audio-to-JSON (multimodal), 
# we bridge it here. If we wanted to do strict ADK from text:

# from google.adk.model import Model
# from google.adk.agent import Agent

# model = Model("gemini-1.5-flash")
# inventory_agent = Agent(model=model, tools=[update_inventory_tool, query_inventory_tool])
# ... but we already have the structured arguments from the Audio model.
