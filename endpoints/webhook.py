from fastapi import APIRouter, Request, Form
from typing import Optional

router = APIRouter()

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    # Basic Twilio webhook structure
    sender = form_data.get("From") # e.g., whatsapp:+923001234567
    media_url = form_data.get("MediaUrl0") # Twilio sends media URLs like this
    media_type = form_data.get("MediaContentType0")
    
    # Twilio Signature Verification (Optional but recommended for Prod)
    # from twilio.request_validator import RequestValidator
    # validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))
    # twilio_signature = request.headers.get("X-Twilio-Signature", "")
    # url = str(request.url)
    # if not validator.validate(url, dict(form_data), twilio_signature):
    #    return {"status": "error", "message": "Invalid signature"}

    print(f"Received message from {sender}, Media: {media_url}, Type: {media_type}")

    if not media_url:
        # Check if it's a text message that we can also process? 
        # For now, MVP focuses on Voice/Image.
        if form_data.get("Body"):
             print("Received text message, ignoring for Voice/Image First MVP")
             return {"status": "ignored", "reason": "text_only"}
        return {"status": "ignored", "reason": "no_media"}
        
    # Process Voice Note or Image
    try:
        from services.gemini_voice import process_media_url
        from services.db import get_tenant_by_phone, add_inventory_log
        import json
        
        # 1. Identify Tenant
        # Remove 'whatsapp:' prefix
        clean_phone = sender.replace("whatsapp:", "")
        # For MVP/Sandboxes, sometimes phone format varies. Robustify?
        tenant = get_tenant_by_phone(clean_phone)
        
        if not tenant:
            print(f"Refused: User {clean_phone} not registered in tenants table.")
            # Optional: Send a "Please Signup" message back
            from twilio.twiml.messaging_response import MessagingResponse
            resp = MessagingResponse()
            resp.message(f"Salaam! Aap registered nahi hain. Please admin se contact karein. ID: {clean_phone}")
            from fastapi.responses import Response
            return Response(content=str(resp), media_type="application/xml")

        # 2. Process Media with Gemini
        extraction_json_str = await process_media_url(media_url, media_type or "")
        
        # Clean up code blocks if Gemini returns them
        extraction_json_str = extraction_json_str.replace("```json", "").replace("```", "")
        # Handle cases where Gemini adds text before/after JSON
        if "{" in extraction_json_str and "}" in extraction_json_str:
            start = extraction_json_str.find("{")
            end = extraction_json_str.rfind("}") + 1
            extraction_json_str = extraction_json_str[start:end]
            
        data = json.loads(extraction_json_str)
        
        # 3. Agentic Routing (Database Update)
        from services.agent_manager import agent_router
        
        # Add tenant_id context
        extraction_data = data
        
        # Execute DB Action
        db_result = await agent_router(tenant['id'], extraction_data)
        
        # 4. Construct Response (The Trust Loop)
        # Use the Roman Urdu summary from Gemini if available
        summary = data.get("summary_for_user")
        
        if not summary:
            # Fallback if Gemini failed to generate summary
            intent = data.get("intent", "UNKNOWN")
            if intent == "UPDATE":
                summary = f"Done: {data.get('item_name')} {data.get('quantity')} {data.get('unit')} {data.get('action')}"
            else:
                summary = "Maaf kijiye, samajh nahi aaya. Dobara boliye."

        # If DB error, append warning
        if isinstance(db_result, dict) and db_result.get("status") == "error":
             summary += f" (Note: System Error - {db_result.get('message')})"

        # Send Reply
        from twilio.twiml.messaging_response import MessagingResponse
        resp = MessagingResponse()
        resp.message(summary)
        
        # Return XML Response for Twilio
        from fastapi.responses import Response
        return Response(content=str(resp), media_type="application/xml")

    except Exception as e:
        print(f"Error processing webhook: {e}")
        # In prod, logging.exception(e)
        return {"status": "error", "message": str(e)}

    return {"status": "received"}
