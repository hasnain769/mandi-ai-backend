import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the 'gemini-2.5-flash' model
model = genai.GenerativeModel('models/gemini-2.5-flash')

import requests
import tempfile

async def process_media_url(media_url: str, media_type: str):
    """
    Downloads media (audio/image) from URL, uploads to Gemini, and requests JSON extraction.
    """
    # Download the file
    # Check if credentials exist for Twilio
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    # Debug logging
    print(f"DEBUG: Downloading media. SID present: {bool(account_sid)}, Token present: {bool(auth_token)}")
    
    auth = None
    if account_sid and auth_token and "twilio.com" in media_url:
        auth = (account_sid, auth_token)

    print(f"DEBUG: Requesting {media_url} with auth: {bool(auth)}")
    headers = {"User-Agent": "Mandi-AI-Bot/1.0"}
    response = requests.get(media_url, auth=auth, headers=headers, allow_redirects=True)
    if response.status_code != 200:
        print(f"Failed to download media: {response.status_code}, URL: {media_url}")
        raise Exception("Failed to download media")

    # Determine extension
    ext = ".ogg" # default for WhatsApp voice
    mime_type = "audio/ogg"
    if "image" in media_type:
        ext = ".jpg"
        mime_type = "image/jpeg"
    
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
        temp_file.write(response.content)
        temp_path = temp_file.name
    
    try:
        # Upload the file to Gemini
        # Note: Gemini 1.5 Flash supports audio and images directly
        gemini_file = genai.upload_file(path=temp_path, mime_type=mime_type)
        
        # Enhanced Prompt for Mandi (Wholesaler) Context
        prompt = """
        You are an intelligent "Digital Munshi" (Clerk) for a Pakistani Mandi wholesaler.
        Your users are illiterate or semi-literate and speak Urdu, Punjabi, or "Mandi Lingo".
        
        **Your Inputs:**
        1. **Voice Notes**: "50 bori aalu aaye hain", "Rashid bhai ko 10 gaddi pyaz bhej di".
        2. **Images**: Handwritten receipts or pictures of stock.

        **Your Task:**
        Extract the inventory intent into structured JSON.
        
        **Intents:**
        1. **SALE**: Selling items to a buyer (Stock OUT).
           - Keywords: "bheje", "sold", "diye", "Rashid ko diye", "rate lagaya".
           - Extract: 
             - `item_name`, `quantity`, `unit`.
             - `buyer_name`: Who bought it? (e.g. "Rashid Bhai").
             - `rate`: Price per unit.
             - `is_credit`: true if "udhaar" or "khaate mein", false if "cash".
        2. **UPDATE**: General Stock Update (IN/OUT) without sale details.
           - Keywords: "aaye", "receive", "gaya" (without buyer/rate).
           - Extract: `item_name`, `quantity`, `unit`, `action` (IN/OUT).
        3. **QUERY**: Asking for stock.
           - Keywords: "kitna hai", "check karo".
        
        **CRITICAL - The Trust Loop:**
        You MUST generate a `summary_for_user` field. This is a text message sent back to the user on WhatsApp.
        - It must be in **Roman Urdu** (Urdu written in English).
        - It must sound like a respectful Munshi.
        - **For Sales**: "Ji Boss, [Buyer] ko [Qty] [Unit] [Item] [Rate] ke rate par de diya. Total: [Amount]."
        - Example: "Ji Boss, Rashid Bhai ko 10 Bori Potato 5000 ke rate par de diye. Total 50,000 ban gaya."

        **Output Format (JSON Only):**
        {
            "intent": "SALE" | "UPDATE" | "QUERY" | "UNKNOWN",
            "item_name": "string" (or null),
            "quantity": number (or null),
            "unit": "string" (or null),
            "action": "IN" | "OUT" (or null),
            "buyer_name": "string" (or null),
            "rate": number (or null),
            "is_credit": boolean (default false),
            "summary_for_user": "string (Roman Urdu response)",
            "original_text": "Transcribed text"
        }
        """
        
        response = model.generate_content([prompt, gemini_file])
        return response.text
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

