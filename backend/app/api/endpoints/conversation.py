from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from backend.app.database.session import get_db
from backend.app.database.models import ConversationMessage
from backend.app.services.conversation_service import conversation_service
from backend.app.nlp.multi_turn_tracker import multi_turn_tracker

router = APIRouter(prefix="/conversation", tags=["Conversation Hub"])

class MessagePayload(BaseModel):
    message: str
    session_id: str = "default_session"
    is_voice: bool = False

class ConfirmationPayload(BaseModel):
    event_dict: Dict[str, Any]
    override_amount: Optional[float] = None
    force_settle: bool = False
    session_id: str = "default_session"
    selected_entity_id: Optional[int] = None
    override_actor: Optional[str] = None
    link_as_alias: bool = True

@router.post("/message")
def send_message(payload: MessagePayload, db: Session = Depends(get_db)):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    result = conversation_service.process_message(
        db=db,
        message_text=payload.message,
        session_id=payload.session_id,
        is_voice=payload.is_voice
    )
    return result

@router.post("/confirm")
def confirm_event(payload: ConfirmationPayload, db: Session = Depends(get_db)):
    result = conversation_service.confirm_and_apply_event(
        db=db,
        event_dict=payload.event_dict,
        override_amount=payload.override_amount,
        force_settle=payload.force_settle,
        selected_entity_id=payload.selected_entity_id,
        override_actor=payload.override_actor,
        link_as_alias=payload.link_as_alias
    )
    return result

@router.get("/history")
def get_conversation_history(session_id: str = "default_session", db: Session = Depends(get_db)):
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).order_by(ConversationMessage.created_at.asc()).all()
    
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "message": m.message_text,
            "is_voice": m.is_voice,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]

@router.post("/reset-session")
def reset_session(session_id: str = "default_session"):
    multi_turn_tracker.clear_session(session_id)
    return {"success": True, "message": f"Session '{session_id}' cleared"}
