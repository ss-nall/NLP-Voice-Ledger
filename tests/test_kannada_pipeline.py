"""
Unit & Integration Tests for Kannada Financial NLP Processing Pipeline.
Tests Kannada Script (Unicode: 0x0C80 - 0x0CFF), Romanized Kannada, Spoken Numerals, Relations, Temporals, and Analytical Queries.
"""

import pytest
from backend.app.nlp.pipeline import nlp_pipeline
from backend.app.nlp.speech_processor import IndicSpokenNumberParser
from backend.app.nlp.language_detection import language_identifier
from backend.app.nlp.query_engine import SemanticQueryEngine

def test_kannada_spoken_number_parsing():
    assert IndicSpokenNumberParser.parse_spoken_number("ondhu nooru") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("ainooru") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("ondhu saavira") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("eradu saavira") == 2000
    assert IndicSpokenNumberParser.parse_spoken_number("aidu saavira") == 5000
    assert IndicSpokenNumberParser.parse_spoken_number("hattusaavira") == 10000
    assert IndicSpokenNumberParser.parse_spoken_number("ondhu laksha") == 100000
    
    # Kannada script numerals
    assert IndicSpokenNumberParser.parse_spoken_number("ನೂರು") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("ಐನೂರು") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("ಸಾವಿರ") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("ಎರಡು ಸಾವಿರ") == 2000

def test_kannada_language_identification():
    res_script = language_identifier.identify("ಮಂಜುನಾಥ್ ನನಗೆ ₹2500 ಕೊಟ್ಟಿದ್ದಾರೆ")
    assert "kannada" in res_script["primary_language"]
    
    res_roman = language_identifier.identify("Manjunath ige aaidu saavira kodabeku naale")
    assert "kannada" in res_roman["primary_language"] or res_roman["primary_language"] in ["romanized_kannada", "code_mixed_kannada", "english"]

def test_kannada_payable_obligation():
    res = nlp_pipeline.process_text("Supplier ige 5000 kodabeku", session_id="test_kn_1")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 5000
    assert ev.event_type == "payable_obligation"

def test_kannada_receivable_obligation():
    res = nlp_pipeline.process_text("Prakash inda 2500 barabeku", session_id="test_kn_2")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2500
    assert "Prakash" in ev.actor

def test_kannada_customer_payment():
    res = nlp_pipeline.process_text("Ramesh 1500 kottaru", session_id="test_kn_3")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 1500
    assert ev.event_type == "partial_payment"
    assert "Ramesh" in ev.actor

def test_kannada_business_payment():
    res = nlp_pipeline.process_text("Naanu Suresh ige 3000 kotte", session_id="test_kn_4")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 3000
    assert ev.event_type in ["partial_payment", "payment_made"]

def test_kannada_promise_payment():
    res = nlp_pipeline.process_text("Anand mundina vaara 4000 kodtini antha helida", session_id="test_kn_5")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 4000
    assert ev.event_type == "payment_commitment"

def test_kannada_script_full_event():
    res = nlp_pipeline.process_text("ಮಂಜುನಾಥ್ ನಿನ್ನೆ 2000 ಕೊಟ್ಟರು", session_id="test_kn_6")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2000
    assert ev.event_type == "partial_payment"

def test_kannada_queries():
    engine = SemanticQueryEngine()
    q1 = engine.parse_query("ಈ ತಿಂಗಳು ಯಾರಿಗೆ ಹೆಚ್ಚು ಕೊಟ್ಟಿದ್ದೇನೆ?")
    assert q1["intent"] == "HIGHEST_OUTFLOW"
    
    q2 = engine.parse_query("ರಮೇಶ್ ಯಾವಾಗ ಪಾವತಿಸಿದರು?")
    assert q2["intent"] == "LAST_PAYMENT_DATE"
    
    q3 = engine.parse_query("ಈ ವಾರ ಬರಬೇಕಾದ ಬಾಕಿ ಎಷ್ಟು?")
    assert q3["intent"] == "WEEKLY_RECEIVABLES"
