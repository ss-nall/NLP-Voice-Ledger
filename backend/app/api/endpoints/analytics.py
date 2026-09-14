from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Financial Analytics"])

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    return analytics_service.get_overview(db)

@router.get("/aging")
def get_aging(db: Session = Depends(get_db)):
    return analytics_service.get_aging_analysis(db)

@router.get("/cashflow")
def get_cashflow_forecast(days: int = 30, db: Session = Depends(get_db)):
    return analytics_service.get_cash_flow_forecast(db, days_ahead=days)

@router.get("/top-debtors")
def get_top_debtors(limit: int = 5, db: Session = Depends(get_db)):
    return analytics_service.get_top_debtors(db, limit=limit)

@router.get("/reminders")
def get_reminders(db: Session = Depends(get_db)):
    return analytics_service.get_reminders(db)

