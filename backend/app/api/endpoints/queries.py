from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.database.session import get_db
from backend.app.services.conversation_service import conversation_service

router = APIRouter(prefix="/queries", tags=["Deterministic NL Queries"])

class QueryRequest(BaseModel):
    query: str
    session_id: str = "query_session"

@router.post("/execute")
def execute_nl_query(payload: QueryRequest, db: Session = Depends(get_db)):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    result = conversation_service.process_message(
        db=db,
        message_text=payload.query,
        session_id=payload.session_id,
        is_voice=False
    )
    return result
