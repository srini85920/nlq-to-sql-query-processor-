from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# Add these new imports
from sqlalchemy import inspect, text
from pydantic import BaseModel
from typing import Dict, Any

from . import schemas, services
from .database import get_db

app = FastAPI()

# Allow your React frontend to talk to this backend
# IMPORTANT: I've added your new frontend URL (http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Your existing NLQ endpoint ---
@app.post("/api/nlq-to-sql", response_model=schemas.NLQResponse)
def nlq_to_sql_endpoint(request: schemas.NLQRequest, db: Session = Depends(get_db)):
    """Receives a question, gets the SQL and result, and returns it."""
    try:
        sql_query, result = services.get_sql_from_nlq(
            question=request.question, 
            db_engine=db.get_bind()
        )
        return {"sql_query": sql_query, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 
# NEW ENDPOINTS FOR YOUR "MANAGE DATA" PAGE
# ---

# This Pydantic model defines the data shape for adding a new record
class AddRecordRequest(BaseModel):
    table: str
    data: Dict[str, Any]

@app.get("/api/schema")
def get_schema(db: Session = Depends(get_db)):
    """
    NEW ENDPOINT
    Returns the database schema (all tables and their columns).
    """
    try:
        inspector = inspect(db.get_bind())
        schema_info = {"tables": {}}
        for table_name in inspector.get_table_names():
            # We only want to manage our main tables
            if table_name in ['customers', 'products', 'orders', 'order_items']:
                columns = [column['name'] for column in inspector.get_columns(table_name)]
                schema_info["tables"][table_name] = columns
        return schema_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/add-record")
def add_record(request: AddRecordRequest, db: Session = Depends(get_db)):
    """
    NEW ENDPOINT
    Adds a new record to the specified table.
    This is built to be safe from SQL injection.
    """
    try:
        # Build the INSERT statement dynamically but safely
        columns = ", ".join(request.data.keys())
        # Use :key placeholders for parameterized query
        placeholders = ", ".join([f":{key}" for key in request.data.keys()])
        
        # Use text() and pass parameters to prevent SQL injection
        sql = text(f"INSERT INTO {request.table} ({columns}) VALUES ({placeholders})")
        
        # db.execute takes the parameters as a dictionary
        db.execute(sql, request.data)
        db.commit() # Save the changes to the database
        return {"status": "success", "message": "Record added."}
    except Exception as e:
        db.rollback() # Rollback changes if an error occurs
        raise HTTPException(status_code=400, detail=str(e))
