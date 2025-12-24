# GEMINI CODE (COMMENTED OUT - Using Groq instead)
# from google import genai
# from config.settings import GEMINI_API_KEYS
# import os
# 
# def list_models_gemini():
#     if not GEMINI_API_KEYS:
#         print("No API Keys found.")
#         return
# 
#     # Try the first key
#     api_key = GEMINI_API_KEYS[0]
#     client = genai.Client(api_key=api_key)
# 
#     try:
#         print(f"Checking models with key: {api_key[:5]}...")
#         # Note: In the new SDK, listing models might be different. 
#         # But commonly it's client.models.list() or similar.
#         # Let's try to just print what we can find or fallback to a standard list if the SDK structure is strictly typed.
#         
#         # Based on documentation for google-genai, let's try to iterate
#         # Assuming client.models.list() exists and returns an iterable
#         for m in client.models.list():
#             print(f"Model: {m.name}")
#             
#     except Exception as e:
#         print(f"Error listing models: {e}")


# NEW GROQ IMPLEMENTATION
from groq import Groq
from config.settings import GROQ_API_KEY
import os

def list_models():
    """List available Groq models"""
    if not GROQ_API_KEY:
        print("No GROQ_API_KEY found.")
        return

    try:
        client = Groq(api_key=GROQ_API_KEY)
        print(f"Checking Groq models...")
        
        # List available models
        models = client.models.list()
        
        print("\nAvailable Groq Models:")
        for model in models.data:
            print(f"  - {model.id}")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
