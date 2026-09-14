import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.session import Base
from backend.app.database.models import (
    Customer, Supplier, Transaction, PaymentCommitment
)
from backend.app.nlp.pipeline import NLPPipeline
from backend.app.nlp.temporal_extraction import TemporalExtractor
from backend.app.services.ledger_service import LedgerService
from backend.app.services.analytics_service import AnalyticsService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_september_17_temporal_and_amount_isolation():
    """
    Verify: 'సెప్టెంబర్ 17 కి పవన్ కి 15,000 ఇవ్వాలి.'
    1. Amount is 15000.0 (NOT 17!)
    2. Actor is Pavan / పవన్
    3. Due Date is 2026-09-17
    4. Direction is payable
    """
    pipeline = NLPPipeline()
    res = pipeline.process_text("సెప్టెంబర్ 17 కి పవన్ కి 15,000 ఇవ్వాలి.")
    event = res.event
    
    assert event.amount == 15000.0
    assert "పవన్" in event.actor
    assert event.direction == "payable"
    assert event.due_date == "2026-09-17"


def test_relative_dates_and_receivables():
    """Verify: 'రేపు రమేష్ నాకు 500 ఇస్తానన్నాడు'"""
    pipeline = NLPPipeline()
    res = pipeline.process_text("రేపు రమేష్ నాకు 500 ఇస్తానన్నాడు")
    event = res.event
    
    assert event.amount == 500.0
    assert "రమేష్" in event.actor
    assert event.direction == "receivable"
    assert event.due_date is not None


def test_telugu_month_extraction_formats():
    """Verify various Telugu calendar date formats."""
    anchor = datetime(2026, 9, 13)
    
    d1 = TemporalExtractor.extract_dates("సెప్టెంబర్ 17 కి", anchor_date=anchor)
    assert len(d1) > 0
    assert d1[0]["normalized_date"] == "2026-09-17"
    assert d1[0]["temporal_role"] == "DUE_DATE"
    
    d2 = TemporalExtractor.extract_dates("అక్టోబర్ 5 న షాప్ అద్దె", anchor_date=anchor)
    assert len(d2) > 0
    assert d2[0]["normalized_date"] == "2026-10-05"
    
    d3 = TemporalExtractor.extract_dates("17 సెప్టెంబర్", anchor_date=anchor)
    assert len(d3) > 0
    assert d3[0]["normalized_date"] == "2026-09-17"


def test_payment_commitment_creation_and_whatsapp_reminder(db_session):
    """
    Verify end-to-end payment commitment creation and WhatsApp message generation.
    """
    pipeline = NLPPipeline()
    res = pipeline.process_text("సెప్టెంబర్ 17 కి పవన్ కి 15,000 ఇవ్వాలి.")
    out = LedgerService.apply_financial_event(db_session, res.event)
    
    assert out["success"] is True
    
    # Check commitment record
    reminders = AnalyticsService.get_reminders(db_session)
    assert len(reminders) == 1
    rem = reminders[0]
    
    assert "పవన్" in rem["entity_name"]
    assert rem["amount"] == 15000.0
    assert rem["due_date"] == "2026-09-17"
    assert "17 సెప్టెంబర్ 2026" in rem["formatted_date_te"]
    assert "₹15,000" in rem["whatsapp_message"]
    assert "wa.me" in rem["whatsapp_link"]
