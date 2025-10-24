from pydantic import BaseModel
from typing import List, Any

# Input schema: What your API expects
class NLQRequest(BaseModel):
    question: str

# Output schema: What your API will send back
class NLQResponse(BaseModel):
    sql_query: str
    result: List[Any]
    error: str = None