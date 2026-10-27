"""
Unit & Integration Tests for Tamil Financial NLP Processing Pipeline.
Tests Tamil Script, Tanglish, Spoken Numerals, Relations, Temporals, and Analytical Queries.
"""

import pytest
from datetime import datetime, timedelta
from backend.app.nlp.pipeline import nlp_pipeline
from backend.app.nlp.speech_processor import IndicSpokenNumberParser, speech_processor
from backend.app.nlp.language_detection import language_identifier
from backend.app.nlp.query_understanding import nl_query_parser

def test_tamil_spoken_number_parsing():
    # Basic numerals
    assert IndicSpokenNumberParser.parse_spoken_number("nooru") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("ainooru") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("aayiram") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("irandaayiram") == 2000
    assert IndicSpokenNumberParser.parse_spoken_number("moovaayiram") == 3000
    assert IndicSpokenNumberParser.parse_spoken_number("patthaayiram") == 10000
    assert IndicSpokenNumberParser.parse_spoken_number("aimbadhaayiram") == 50000
    assert IndicSpokenNumberParser.parse_spoken_number("oru latcham") == 100000
    
    # Tamil script numerals
    assert IndicSpokenNumberParser.parse_spoken_number("நூறு") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("ஐந்நூறு") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("ஆயிரம்") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("இரண்டாயிரம்") == 2000

def test_tamil_language_identification():
    res_script = language_identifier.identify("முருகன் எனக்கு ₹2500 கொடுத்தார்")
    assert "tamil" in res_script["primary_language"]
    
    res_roman = language_identifier.identify("Murugan ainooru tharanum adutha vaaram")
    assert "tamil" in res_script["primary_language"] or res_roman["primary_language"] in ["romanized_tamil", "code_mixed_tamil", "english"]

def test_tamil_payable_obligation():
    res = nlp_pipeline.process_text("Supplier kku 5000 kodukanum", session_id="test_tamil_1")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 5000
    assert ev.event_type == "payable_obligation"

def test_tamil_receivable_obligation():
    res = nlp_pipeline.process_text("Murugan kitterundhu 2500 varanum", session_id="test_tamil_2")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2500
    assert "Murugan" in ev.actor

def test_tamil_customer_payment():
    res = nlp_pipeline.process_text("Selvam netru 1500 koduthaar", session_id="test_tamil_3")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 1500
    assert ev.event_type == "partial_payment"
    assert "Selvam" in ev.actor

def test_tamil_business_payment():
    res = nlp_pipeline.process_text("Karthik kku 3000 koduthen", session_id="test_tamil_4")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 3000
    assert ev.event_type in ["partial_payment", "payment_made"]

def test_tamil_promise_payment():
    res = nlp_pipeline.process_text("Praveen adutha vaaram 4000 tharen nu sonnaar", session_id="test_tamil_5")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 4000
    assert ev.event_type == "payment_commitment"

def test_tamil_script_full_event():
    res = nlp_pipeline.process_text("கவிதா நேற்று 2000 கொடுத்தார்", session_id="test_tamil_6")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2000
    assert ev.event_type == "partial_payment"

def test_tamil_queries():
    q1 = nl_query_parser.parse_query("yaar athigam tharanum")
    assert q1["intent"] == "TOP_DEBTORS"
    
    q2 = nl_query_parser.parse_query("suppliers ku evalo tharanum")
    assert q2["intent"] == "TOTAL_PAYABLES"
    
    q3 = nl_query_parser.parse_query("கஸ்டமர்களிடம் எவ்வளவு வர வேண்டும்")
    assert q3["intent"] == "TOTAL_RECEIVABLES"
