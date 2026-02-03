import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin
# Expects GOOGLE_APPLICATION_CREDENTIALS env var to point to the service account key
# OR explicit path in .env
cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

if not firebase_admin._apps:
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback to default search or raising error in production
        print("Warning: Firebase Service Account not found. Auth verification will fail.")
        # firebase_admin.initialize_app() 

def verify_token(id_token: str):
    """
    Verifies a Firebase ID token.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None
