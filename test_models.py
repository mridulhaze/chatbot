import os
import sys
from pathlib import Path
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing supported Gemini models for current API key:")
try:
    for m in client.models.list():
        if "gemini" in m.name.lower():
            print(f" - {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
