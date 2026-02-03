import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

supabase: Client = create_client(url, key)

def seed_user(phone_number: str):
    print(f"Seeding user: {phone_number}...")
    
    # Check if exists
    response = supabase.table("tenants").select("*").eq("phone_number", phone_number).execute()
    if response.data:
        print("User already exists!")
        print(response.data[0])
        return

    # Insert
    data = {
        "phone_number": phone_number,
        "business_name": "Test Mandi Shop"
    }
    response = supabase.table("tenants").insert(data).execute()
    print("User created successfully!")
    print(response.data)

if __name__ == "__main__":
    # Default test number. Update this if you use true real number.
    # Format must match what comes from Twilio/Firebase
    # Usually Twilio sends 'whatsapp:+92...'
    # Our webhook strips 'whatsapp:', so we store '+92...'
    TEST_PHONE = "+923436765503" 
    seed_user(TEST_PHONE)
