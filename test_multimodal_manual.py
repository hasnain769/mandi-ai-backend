import asyncio
import os
from services.gemini_voice import process_media_url
from dotenv import load_dotenv

load_dotenv()

async def test_multimodal():
    # 1. Test Audio (Simulated)
    # Using a public sample audio file or assume one exists. 
    # For this test, we might need a real URL.
    # Let's use a dummy URL and mock the download in a real test, 
    # but here we want to test the GEMINI integration.
    
    # Since we can't easily get a public URL for a specific Urdu voice note,
    # we will modify this test to USE A LOCAL FILE if possible, 
    # OR we skip the download part if we modify the service to accept path.
    # But `process_media_url` takes a URL.
    
    print("--- Testing Audio Processing ---")
    try:
        # This is a sample OGG file
        audio_url = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Example.ogg" 
        print(f"Processing Audio: {audio_url}")
        result = await process_media_url(audio_url, "audio/ogg")
        print("\nGemini Audio Result:")
        print(result)
    except Exception as e:
        print(f"Audio Test Failed (Expected if Gemini API key missing or URL issue): {e}")

    # 2. Test Image (Receipt)
    print("\n--- Testing Image Processing ---")
    try:
        # Sample receipt image
        image_url = "https://upload.wikimedia.org/wikipedia/commons/0/0b/ReceiptSwiss.jpg"
        print(f"Processing Image: {image_url}")
        result = await process_media_url(image_url, "image/jpeg")
        print("\nGemini Image Result:")
        print(result)
    except Exception as e:
        print(f"Image Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_multimodal())
