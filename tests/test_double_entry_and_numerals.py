import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.session import Base
from backend.app.database.models import (
    Customer, Supplier, Transaction, JournalEntry, JournalLineItem
)
from backend.app.nlp.pipeline import NLPPipeline
from backend.app.nlp.speech_processor import TeluguSpokenNumberParser
from backend.app.nlp.transliteration import split_telugu_sandhi, get_bilingual_names
from backend.app.services.ledger_service import LedgerService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_formatted_comma_number_parsing():
    """Verify that numbers with commas are not split into additive sub-tokens."""
    assert TeluguSpokenNumberParser.parse_spoken_number("50,000") == 50000
    assert TeluguSpokenNumberParser.parse_spoken_number("1,50,000") == 150000
    assert TeluguSpokenNumberParser.parse_spoken_number("10,00,000") == 1000000
    assert TeluguSpokenNumberParser.parse_spoken_number("50,000.50") == 50000.50
    assert TeluguSpokenNumberParser.parse_spoken_number("25k") == 25000


def test_spoken_telugu_numeral_parsing():
    """Verify spoken Telugu numbers."""
    assert TeluguSpokenNumberParser.parse_spoken_number("యాభై వేలు") == 50000
    assert TeluguSpokenNumberParser.parse_spoken_number("పదివేలు") == 10000
    assert TeluguSpokenNumberParser.parse_spoken_number("ఇరవైవేలు") == 20000
    assert TeluguSpokenNumberParser.parse_spoken_number("oka laksha") == 100000
    assert TeluguSpokenNumberParser.parse_spoken_number("5 thouzad") == 5000


def test_split_telugu_sandhi_expansions():
    """Verify sandhi splitting for numerals, verbs, pronouns, and entities."""
    assert "50,000 ఇచ్చేశాను" in split_telugu_sandhi("50,000ఇచ్చేశాను")
    assert "నాకు ఇచ్చాడు" in split_telugu_sandhi("నాకిచ్చాడు")
    assert "నాకు వచ్చింది" in split_telugu_sandhi("నాకొచ్చింది")
    assert "ప్రేమ్ కి ఇచ్చాను" in split_telugu_sandhi("ప్రేమ్కిచ్చాను")
    assert "పదివేలు ఇచ్చాడు" in split_telugu_sandhi("పదివేలిచ్చాడు")


def test_bilingual_name_brackets():
    """Verify bracketed transliteration format."""
    te_res = get_bilingual_names("ప్రేమ్")
    assert te_res["display"] == "ప్రేమ్ (Prem)"
    
    en_res = get_bilingual_names("Prem")
    assert en_res["display"] == "Prem (ప్రేమ్)"


def test_prem_statement_nlp_pipeline():
    """Verify pipeline output for 'ప్రేమ్ కి 50,000 ఇచ్చేశాను.'"""
    pipeline = NLPPipeline()
    result = pipeline.process_text("ప్రేమ్ కి 50,000 ఇచ్చేశాను.")
    event = result.event
    
    assert event.amount == 50000.0
    assert "ప్రేమ్" in event.actor
    assert event.direction == "payable"
    assert event.event_type in ["payment_made", "partial_payment"]


def test_double_entry_journal_lifecycle_and_balance(db_session):
    """
    Verify complete double-entry bookkeeping cycle:
    1. Credit Sale: Ramesh owes ₹10,000 (Dr AR, Cr Sales)
    2. Partial Payment: Ramesh pays ₹4,000 (Dr Cash, Cr AR)
    3. Health check: Total Debits == Total Credits, AR = ₹6,000
    """
    pipeline = NLPPipeline()
    
    # 1. Credit Sale
    res1 = pipeline.process_text("రమేష్ కి ₹10,000 సరుకు అమ్మాను")
    out1 = LedgerService.apply_financial_event(db_session, res1.event)
    assert out1["current_balance"] == 10000.0
    
    # 2. Payment Received
    res2 = pipeline.process_text("రమేష్ నాకు 4,000 ఇచ్చాడు")
    out2 = LedgerService.apply_financial_event(db_session, res2.event)
    assert out2["current_balance"] == 6000.0
    
    # 3. Verify Double Entry Invariants
    health = LedgerService.check_ledger_health(db_session)
    assert health["is_healthy"] is True
    assert health["trial_balance_balanced"] is True
    assert health["total_debits"] == health["total_credits"]
    assert health["total_debits"] == 14000.0  # 10000 sale + 4000 cash receipt
    assert health["customer_receivables_total"] == 6000.0
    
    # 4. Verify Journal Line Items
    entries = LedgerService.get_journal_entries(db_session)
    assert len(entries) == 2
    for entry in entries:
        assert entry["is_balanced"] is True
        assert len(entry["lines"]) == 2
        debits = sum(l["debit"] for l in entry["lines"])
        credits = sum(l["credit"] for l in entry["lines"])
        assert debits == credits


def test_supplier_payment_double_entry(db_session):
    """
    Verify supplier payable cycle:
    1. Prem purchase: We owe ₹50,000 (Dr Purchases, Cr AP)
    2. Payment made: We pay ₹50,000 (Dr AP, Cr Cash)
    3. AP balance settles to 0.0
    """
    pipeline = NLPPipeline()
    
    # 1. Purchase
    res1 = pipeline.process_text("ప్రేమ్ దగ్గర 50,000 సరుకు కొన్నాను")
    out1 = LedgerService.apply_financial_event(db_session, res1.event)
    assert out1["current_balance"] == 50000.0
    
    # 2. Payment Made
    res2 = pipeline.process_text("ప్రేమ్ కి 50,000 ఇచ్చేశాను.")
    out2 = LedgerService.apply_financial_event(db_session, res2.event)
    assert out2["current_balance"] == 0.0
    
    # 3. Health check
    health = LedgerService.check_ledger_health(db_session)
    assert health["is_healthy"] is True
    assert health["supplier_payables_total"] == 0.0
    assert health["total_debits"] == health["total_credits"]
