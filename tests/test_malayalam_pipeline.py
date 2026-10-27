"""
Unit & Integration Tests for Malayalam Financial NLP Processing Pipeline.
Tests Malayalam Script (Unicode: 0x0D00 - 0x0D7F), Romanized Malayalam, Spoken Numerals, Relations, Temporals, and Analytical Queries.
"""

import pytest
from backend.app.nlp.pipeline import nlp_pipeline
from backend.app.nlp.speech_processor import IndicSpokenNumberParser
from backend.app.nlp.language_detection import language_identifier
from backend.app.nlp.query_engine import SemanticQueryEngine

def test_malayalam_spoken_number_parsing():
    assert IndicSpokenNumberParser.parse_spoken_number("nooru") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("anchooru") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("aayiram") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("randaayiram") == 2000
    assert IndicSpokenNumberParser.parse_spoken_number("anchaayiram") == 5000
    assert IndicSpokenNumberParser.parse_spoken_number("pathinaayiram") == 10000
    assert IndicSpokenNumberParser.parse_spoken_number("laksham") == 100000
    
    # Malayalam script numerals
    assert IndicSpokenNumberParser.parse_spoken_number("നൂറ്") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("അഞ്ഞൂറ്") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("ആയിരം") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("രണ്ടായിരം") == 2000

def test_malayalam_language_identification():
    res_script = language_identifier.identify("മോഹൻ എനിക്ക് ₹2500 തന്നു")
    assert "malayalam" in res_script["primary_language"]
    
    res_roman = language_identifier.identify("Mohan kku 5000 kodukkanam naale")
    assert "malayalam" in res_roman["primary_language"] or res_roman["primary_language"] in ["romanized_malayalam", "code_mixed_malayalam", "code_mixed_tamil", "english"]

def test_malayalam_payable_obligation():
    res = nlp_pipeline.process_text("Supplier kku 5000 kodukkanam", session_id="test_ml_1")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 5000
    assert ev.event_type == "payable_obligation"

def test_malayalam_receivable_obligation():
    res = nlp_pipeline.process_text("Pradeep ninnu 2500 tharanund", session_id="test_ml_2")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2500
    assert "Pradeep" in ev.actor

def test_malayalam_customer_payment():
    res = nlp_pipeline.process_text("Rahul 1500 thannu", session_id="test_ml_3")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 1500
    assert ev.event_type == "partial_payment"
    assert "Rahul" in ev.actor

def test_malayalam_business_payment():
    res = nlp_pipeline.process_text("Njan Vijayan kku 3000 koduthu", session_id="test_ml_4")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 3000
    assert ev.event_type in ["partial_payment", "payment_made"]

def test_malayalam_promise_payment():
    res = nlp_pipeline.process_text("Anil adutha aazhcha 4000 tharaam ennu paranju", session_id="test_ml_5")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 4000
    assert ev.event_type == "payment_commitment"

def test_malayalam_script_full_event():
    res = nlp_pipeline.process_text("രമേഷ് ഇന്നലെ 2000 തന്നു", session_id="test_ml_6")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2000
    assert ev.event_type == "partial_payment"

def test_malayalam_queries():
    engine = SemanticQueryEngine()
    q1 = engine.parse_query("ഈ മാസം ആർക്കാണ് കൂടുതൽ കൊടുത്തത്?")
    assert q1["intent"] == "HIGHEST_OUTFLOW"
    
    q2 = engine.parse_query("രമേഷ് അവസാനം എപ്പോഴാണ് നൽകിയത്?")
    assert q2["intent"] == "LAST_PAYMENT_DATE"
    
    q3 = engine.parse_query("ഈ ആഴ്ച ലഭിക്കാനുള്ള ബാക്കി എത്ര?")
    assert q3["intent"] == "WEEKLY_RECEIVABLES"
