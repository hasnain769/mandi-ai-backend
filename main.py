from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Mandi-AI Backend")

from fastapi.middleware.cors import CORSMiddleware

# CORS Configuration
# In production, set ALLOWED_ORIGINS to your Vercel URL (e.g. "https://mandi-ai.vercel.app")
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mandi-AI Backend is running"}

# Import and include routers
# Import and include routers
from endpoints import webhook, auth, api
app.include_router(webhook.router)
app.include_router(auth.router)
app.include_router(api.router)
