import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

print("--- Starting Database Connection Test ---")

# Load environment variables from .env file
load_dotenv()
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print(" ERROR: DATABASE_URL not found in .env file.")
else:
    print(f"Found DATABASE_URL. Attempting to connect...")
    try:
        # Create an engine to connect to the database
        engine = create_engine(db_url)

        # Try to establish a connection
        with engine.connect() as connection:
            # If connection is successful, run a simple query
            result = connection.execute(text("SELECT 1"))
            print("SUCCESS: Database connection is working correctly!")

    except Exception as e:
        print(" FAILED: Could not connect to the database.")
        print(f"   ERROR DETAILS: {e}")

print("--- Test Finished ---")
