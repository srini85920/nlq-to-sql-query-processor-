import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

print("--- Starting Google API Key Test ---")

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file.")
else:
    print("Found GOOGLE_API_KEY. Attempting to call the API...")
    try:
        # Initialize the LLM with the key
        llm = ChatGoogleGenerativeAI(model="models/gemini-pro-latest")

        # Ask a very simple question
        response = llm.invoke("In one word, what is the color of the sky?")

        print("✅ SUCCESS: API Key is working correctly!")
        print(f"   LLM Response: {response.content}")

    except Exception as e:
        print("❌ FAILED: Could not connect to the Google API.")
        print(f"   ERROR DETAILS: {e}")

print("--- Test Finished ---")