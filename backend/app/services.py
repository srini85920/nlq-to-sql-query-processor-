import os
from dotenv import load_dotenv
from sqlalchemy.engine import Engine
from sqlalchemy import text

# We will use Google's own library directly
import google.generativeai as genai

load_dotenv()

# --- 1. Configure and initialize the Gemini API ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm = genai.GenerativeModel('models/gemini-pro-latest') # Use a valid model from your list

def get_manual_schema_description():
    """
    Manually creates a string describing the database schema.
    This is the context we give to the LLM.
    """
    return """
    You are a PostgreSQL expert. Based on the schema below, convert the user's question to a SQL query.
    
    Database Schema:
    Table: customers (Columns: customer_id, first_name, last_name, email)
    Table: products (Columns: product_id, product_name, category, price)
    Table: orders (Columns: order_id, customer_id, order_date, total_amount)
    Table: order_items (Columns: order_item_id, order_id, product_id, quantity)
    """

def get_sql_from_nlq(question: str, db_engine: Engine):
    """
    Generates and executes SQL from a question WITHOUT LangChain.
    """
    # --- Step 1: Get the schema and create a detailed prompt ---
    schema_description = get_manual_schema_description()
    prompt = f"{schema_description}\n\nUser's Question: {question}\n\nSQL Query:"

    # --- Step 2: Call the Gemini API to get the SQL query ---
    print("--- Calling Gemini API ---")
    response = llm.generate_content(prompt)
    sql_query = response.text.strip().replace("```sql", "").replace("```", "")
    print(f"--- Generated SQL: {sql_query} ---")

    # --- Step 3: Execute the SQL query directly ---
    with db_engine.connect() as connection:
        result = connection.execute(text(sql_query))
        # Convert the database result into a list of dictionaries so it can be sent as JSON
        result_as_list = [dict(row._mapping) for row in result]

    print(f"--- Query Result: {result_as_list} ---")
    return sql_query, result_as_list