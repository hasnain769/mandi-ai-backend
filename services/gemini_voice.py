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

async def process_audio_url(media_url: str):
    """
    Downloads audio from URL, uploads to Gemini, and requests JSON extraction.
    """
    # Download the file
    # Check if credentials exist for Twilio
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    # Debug logging
    print(f"DEBUG: Downloading media. SID present: {bool(account_sid)}, Token present: {bool(auth_token)}")
    if account_sid:
        print(f"DEBUG: SID starts with: {account_sid[:4]}...")
    
    auth = None
    if account_sid and auth_token and "twilio.com" in media_url:
        auth = (account_sid, auth_token)

    print(f"DEBUG: Requesting {media_url} with auth: {bool(auth)}")
    response = requests.get(media_url, auth=auth, allow_redirects=True)
    if response.status_code != 200:
        print(f"Failed to download media: {response.status_code}, URL: {media_url}")
        raise Exception("Failed to download media")

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_audio:
        temp_audio.write(response.content)
        temp_path = temp_audio.name
    
    try:
        # Upload the file
        audio_file = genai.upload_file(path=temp_path)
        
        # Enhanced Prompt for Urdu/English Mixed Audio
        prompt = """
        You are an intelligent Mandi (wholesaler) staff assistant. 
        Your task is to listen to the provided audio (which may be in Urdu, Punjabi, English, or a mix) and extract the user's intent to manage inventory.

        **Intents:**
        1. **UPDATE**: The user wants to ADD or REMOVE stock. 
           - Look for keywords like "aalo aaye hain" (potatoes arrived), "pyaz bhej diye" (onions sent), "add", "remove", "stock in", "sale".
           - Extract: 
             - `item_name`: The vegetable/fruit name (e.g., Potato, Tomato, Onion). normalize to English.
             - `quantity`: The numeric amount.
             - `unit`: The unit (kg, mun, sack, bori, crat).
             - `action`: "IN" (stock arriving/added) or "OUT" (stock sold/removed).
        
        2. **QUERY**: The user is asking about current stock levels.
           - Look for keywords like "kitne hain" (how many), "stock check karo", "batao".
           - Extract:
             - `item_name`: The item they are asking about.

        **Constraint:**
        - Return ONLY a valid JSON object. Do not add markdown backticks or explanations.
        - If the audio is unclear, return `{"intent": "UNKNOWN", "original_text": "description of noise"}`.

        **Output Format:**
        {
            "intent": "UPDATE" | "QUERY" | "UNKNOWN",
            "item_name": "string" (or null),
            "quantity": number (or null),
            "unit": "string" (or null),
            "action": "IN" | "OUT" (or null),
            "original_text": "Transcribed text in Urdu/English script"
        }
        """
        
        response = model.generate_content([prompt, audio_file])
        return response.text
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

