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

    if not media_url or "audio" not in media_type:
        return {"status": "ignored", "reason": "not_audio"}
        
    # Process Voice Note
    try:
        from services.gemini_voice import process_audio_url
        from services.db import get_tenant_by_phone, add_inventory_log
        import json
        
        # 1. Identify Tenant
        # Remove 'whatsapp:' prefix
        clean_phone = sender.replace("whatsapp:", "")
        tenant = get_tenant_by_phone(clean_phone)
        
        if not tenant:
            print(f"Refused: User {clean_phone} not registered in tenants table.")
            return {"status": "error", "message": "User not registered"}

        # 2. Process Audio with Gemini
        # We need to download the file or pass URL if Gemini supports it. 
        # Gemini Python SDK usually needs a file or a file-like object. 
        # For this prototype, let's assume we download it to a temp file.
        # But wait, gemini_voice.py needs update to handle download.
        
        extraction_json_str = await process_audio_url(media_url)
        # Clean up code blocks if Gemini returns them
        extraction_json_str = extraction_json_str.replace("```json", "").replace("```", "")
        data = json.loads(extraction_json_str)
        
        # 3. Agentic Routing
        from services.agent_manager import agent_router
        
        # Add tenant_id context
        extraction_data = data
        
        result = await agent_router(tenant['id'], extraction_data)
        
        # For Twilio, we might want to return a message to the user
        response_text = result.get("message", "Processed")
        
        # If using Twilio MessagingResponse to reply:
        from twilio.twiml.messaging_response import MessagingResponse
        resp = MessagingResponse()
        resp.message(response_text)
        
        # Return XML Response for Twilio
        from fastapi.responses import Response
        return Response(content=str(resp), media_type="application/xml")

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "received"}
