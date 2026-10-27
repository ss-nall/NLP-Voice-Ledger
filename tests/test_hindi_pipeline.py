"""
Unit & Integration Tests for Hindi Financial NLP Processing Pipeline.
Tests Devanagari Hindi Script, Hinglish, Spoken Numerals, Relations, Temporals, and Analytical Queries.
"""

import pytest
from datetime import datetime, timedelta
from backend.app.nlp.pipeline import nlp_pipeline
from backend.app.nlp.speech_processor import IndicSpokenNumberParser
from backend.app.nlp.language_detection import language_identifier
from backend.app.nlp.query_understanding import nl_query_parser

def test_hindi_spoken_number_parsing():
    # Basic numerals
    assert IndicSpokenNumberParser.parse_spoken_number("ek sau") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("paanch sau") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("ek hazaar") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("dedh hazaar") == 1500
    assert IndicSpokenNumberParser.parse_spoken_number("do hazaar") == 2000
    assert IndicSpokenNumberParser.parse_spoken_number("dhai hazaar") == 2500
    assert IndicSpokenNumberParser.parse_spoken_number("das hazaar") == 10000
    assert IndicSpokenNumberParser.parse_spoken_number("pachaas hazaar") == 50000
    assert IndicSpokenNumberParser.parse_spoken_number("ek lakh") == 100000
    
    # Devanagari script numerals
    assert IndicSpokenNumberParser.parse_spoken_number("सौ") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("पांच सौ") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("हजार") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("दो हजार") == 2000

def test_hindi_language_identification():
    res_script = language_identifier.identify("राहुल ने मुझे ₹2500 दिया")
    assert "hindi" in res_script["primary_language"]
    
    res_roman = language_identifier.identify("Amit se paanch sau lena hai agle hafte")
    assert "hindi" in res_roman["primary_language"] or res_roman["primary_language"] in ["romanized_hindi", "code_mixed_hindi", "english"]

def test_hindi_payable_obligation():
    res = nlp_pipeline.process_text("Supplier ko 5000 dena hai", session_id="test_hindi_1")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 5000
    assert ev.event_type == "payable_obligation"

def test_hindi_receivable_obligation():
    res = nlp_pipeline.process_text("Rahul se 2500 lena hai", session_id="test_hindi_2")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2500
    assert "Rahul" in ev.actor

def test_hindi_customer_payment():
    res = nlp_pipeline.process_text("Amit ne kal 1500 diya", session_id="test_hindi_3")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 1500
    assert ev.event_type == "partial_payment"
    assert "Amit" in ev.actor

def test_hindi_business_payment():
    res = nlp_pipeline.process_text("Vikram ko maine 3000 diya", session_id="test_hindi_4")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 3000
    assert ev.event_type in ["partial_payment", "payment_made"]

def test_hindi_promise_payment():
    res = nlp_pipeline.process_text("Rohit agle hafte 4000 dega bola", session_id="test_hindi_5")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 4000
    assert ev.event_type == "payment_commitment"

def test_hindi_script_full_event():
    res = nlp_pipeline.process_text("राहुल ने कल 2000 जमा किया", session_id="test_hindi_6")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2000
    assert ev.event_type == "partial_payment"

def test_hindi_queries():
    q1 = nl_query_parser.parse_query("sabse zyada kisse lena hai")
    assert q1["intent"] == "TOP_DEBTORS"
    
    q2 = nl_query_parser.parse_query("suppliers ko kitna dena hai")
    assert q2["intent"] == "TOTAL_PAYABLES"
    
    q3 = nl_query_parser.parse_query("कस्टमर्स से कितना लेना है")
    assert q3["intent"] == "TOTAL_RECEIVABLES"
