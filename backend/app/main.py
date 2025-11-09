from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from sqlalchemy import inspect, text
from pydantic import BaseModel
from typing import Dict, Any

from . import schemas, services
from .database import get_db

from service import nlq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #this is cors we can allow what ever url needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

#end points
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

@app.post("/nlq")
def handle_nlq(request: NLQRequest):
    return generate_sql_from_nlq(request.question)


@app.post("/api/add-record")
def add_record(request: AddRecordRequest, db: Session = Depends(get_db)):
    """
    NEW ENDPOINT
    Adds a new record to the specified table.
    This is built to be safe from SQL injection.
    """
    try:
      
        columns = ", ".join(request.data.keys())
      
        placeholders = ", ".join([f":{key}" for key in request.data.keys()])
        
        sql = text(f"INSERT INTO {request.table} ({columns}) VALUES ({placeholders})")
        
      
        db.execute(sql, request.data)
        db.commit()
        return {"status": "success", "message": "Record added."}
    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=400, detail=str(e))
