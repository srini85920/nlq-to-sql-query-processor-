import os
from dotenv import load_dotenv
import google.generativeai as genai

# You might need to install this library first:
# pip install google-generativeai

print("--- Listing available Google AI Models ---")
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file.")
else:
    try:
        genai.configure(api_key=api_key)
        print("✅ SUCCESS: Found the following models you can use:")
        for m in genai.list_models():
            # Check if the model supports the 'generateContent' method
            if 'generateContent' in m.supported_generation_methods:
                print(f"  -> {m.name}")
    except Exception as e:
        print(f"❌ FAILED: An error occurred: {e}")

print("--- Script Finished ---")