"""
Unit & Integration Tests for Urdu Financial NLP Processing Pipeline.
Tests Urdu/Arabic Script (Unicode: 0x0600 - 0x06FF), Romanized Urdu, Spoken Numerals, Relations, Temporals, and Analytical Queries.
"""

import pytest
from backend.app.nlp.pipeline import nlp_pipeline
from backend.app.nlp.speech_processor import IndicSpokenNumberParser
from backend.app.nlp.language_detection import language_identifier
from backend.app.nlp.query_engine import SemanticQueryEngine

def test_urdu_spoken_number_parsing():
    assert IndicSpokenNumberParser.parse_spoken_number("ek sau") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("paanch sau") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("ek hazaar") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("do hazaar") == 2000
    assert IndicSpokenNumberParser.parse_spoken_number("paanch hazaar") == 5000
    assert IndicSpokenNumberParser.parse_spoken_number("das hazaar") == 10000
    assert IndicSpokenNumberParser.parse_spoken_number("ek laakh") == 100000
    
    # Urdu script numerals
    assert IndicSpokenNumberParser.parse_spoken_number("سو") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("پانچ سو") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("ہزار") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("دو ہزار") == 2000

def test_urdu_language_identification():
    res_script = language_identifier.identify("طارق نے مجھے ۲۵۰۰ روپے دیے")
    assert "urdu" in res_script["primary_language"]
    
    res_roman = language_identifier.identify("Tariq ko 5000 dena hai kal")
    assert "urdu" in res_roman["primary_language"] or res_roman["primary_language"] in ["romanized_urdu", "code_mixed_urdu", "english", "romanized_hindi", "code_mixed_hindi"]

def test_urdu_payable_obligation():
    res = nlp_pipeline.process_text("Supplier ko 5000 dena hai", session_id="test_ur_1")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 5000
    assert ev.event_type == "payable_obligation"

def test_urdu_receivable_obligation():
    res = nlp_pipeline.process_text("Aslam se 2500 lena hai", session_id="test_ur_2")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2500
    assert "Aslam" in ev.actor

def test_urdu_customer_payment():
    res = nlp_pipeline.process_text("Farhan ne kal 1500 diya", session_id="test_ur_3")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 1500
    assert ev.event_type == "partial_payment"
    assert "Farhan" in ev.actor

def test_urdu_business_payment():
    res = nlp_pipeline.process_text("Maine Bilal ko 3000 diya", session_id="test_ur_4")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 3000
    assert ev.event_type in ["partial_payment", "payment_made"]

def test_urdu_promise_payment():
    res = nlp_pipeline.process_text("Zubair agle hafte 4000 dega bola", session_id="test_ur_5")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 4000
    assert ev.event_type == "payment_commitment"

def test_urdu_script_full_event():
    res = nlp_pipeline.process_text("رمیش نے کل 2000 جمع کیا", session_id="test_ur_6")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2000
    assert ev.event_type == "partial_payment"

def test_urdu_queries():
    engine = SemanticQueryEngine()
    q1 = engine.parse_query("اس مہینے کس کو سب سے زیادہ دیا؟")
    assert q1["intent"] == "HIGHEST_OUTFLOW"
    
    q2 = engine.parse_query("رمیش نے پچھلی بار کب ادائیگی کی؟")
    assert q2["intent"] == "LAST_PAYMENT_DATE"
    
    q3 = engine.parse_query("اس ہفتے کتنی رقم لینی ہے؟")
    assert q3["intent"] == "WEEKLY_RECEIVABLES"
