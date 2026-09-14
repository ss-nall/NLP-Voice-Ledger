from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.app.services.reminder_service import reminder_service

router = APIRouter(prefix="/reminders", tags=["Payment Reminders"])

class ReminderRequest(BaseModel):
    customer_name: str
    amount: float
    due_date: str
    phone: Optional[str] = ""
    store_name: Optional[str] = "Sri Lakshmi Kirana"

@router.post("/generate")
def generate_reminder(payload: ReminderRequest):
    if not payload.customer_name or payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid customer name or amount")
        
    return reminder_service.generate_reminders(
        customer_name=payload.customer_name,
        amount=payload.amount,
        due_date=payload.due_date,
        phone=payload.phone or "",
        store_name=payload.store_name or "Sri Lakshmi Kirana"
    )
