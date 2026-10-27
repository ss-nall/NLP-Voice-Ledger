"""
Unit & Integration Tests for Gujarati Financial NLP Processing Pipeline.
Tests Gujarati Script (Unicode: 0x0A80 - 0x0AFF), Romanized Gujarati, Spoken Numerals, Relations, Temporals, and Analytical Queries.
"""

import pytest
from backend.app.nlp.pipeline import nlp_pipeline
from backend.app.nlp.speech_processor import IndicSpokenNumberParser
from backend.app.nlp.language_detection import language_identifier
from backend.app.nlp.query_engine import SemanticQueryEngine

def test_gujarati_spoken_number_parsing():
    assert IndicSpokenNumberParser.parse_spoken_number("so") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("paanchso") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("ek hajar") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("behajar") == 2000
    assert IndicSpokenNumberParser.parse_spoken_number("paanchhajar") == 5000
    assert IndicSpokenNumberParser.parse_spoken_number("dashajar") == 10000
    assert IndicSpokenNumberParser.parse_spoken_number("ek laakh") == 100000
    
    # Gujarati script numerals
    assert IndicSpokenNumberParser.parse_spoken_number("સો") == 100
    assert IndicSpokenNumberParser.parse_spoken_number("પાંચસો") == 500
    assert IndicSpokenNumberParser.parse_spoken_number("હજાર") == 1000
    assert IndicSpokenNumberParser.parse_spoken_number("બે હજાર") == 2000

def test_gujarati_language_identification():
    res_script = language_identifier.identify("ભાવેશે મને ₹2500 આપ્યા")
    assert "gujarati" in res_script["primary_language"]
    
    res_roman = language_identifier.identify("Bhavesh ne 5000 aapvana che kale")
    assert "gujarati" in res_roman["primary_language"] or res_roman["primary_language"] in ["romanized_gujarati", "code_mixed_gujarati", "english"]

def test_gujarati_payable_obligation():
    res = nlp_pipeline.process_text("Supplier ne 5000 aapvana che", session_id="test_gu_1")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 5000
    assert ev.event_type == "payable_obligation"

def test_gujarati_receivable_obligation():
    res = nlp_pipeline.process_text("Paresh pasethi 2500 levana che", session_id="test_gu_2")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2500
    assert "Paresh" in ev.actor

def test_gujarati_customer_payment():
    res = nlp_pipeline.process_text("Jignesh kale 1500 aapya", session_id="test_gu_3")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 1500
    assert ev.event_type == "partial_payment"
    assert "Jignesh" in ev.actor

def test_gujarati_business_payment():
    res = nlp_pipeline.process_text("Me Hitesh ne 3000 aapya", session_id="test_gu_4")
    ev = res.event
    assert ev.direction == "payable"
    assert ev.amount == 3000
    assert ev.event_type in ["partial_payment", "payment_made"]

def test_gujarati_promise_payment():
    res = nlp_pipeline.process_text("Kiran aavta athwade 4000 aapshe bolya", session_id="test_gu_5")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 4000
    assert ev.event_type == "payment_commitment"

def test_gujarati_script_full_event():
    res = nlp_pipeline.process_text("રમેશે કાલે 2000 જમા કર્યા", session_id="test_gu_6")
    ev = res.event
    assert ev.direction == "receivable"
    assert ev.amount == 2000
    assert ev.event_type == "partial_payment"

def test_gujarati_queries():
    engine = SemanticQueryEngine()
    q1 = engine.parse_query("આ મહિને સૌથી વધુ કોને ચૂકવ્યા?")
    assert q1["intent"] == "HIGHEST_OUTFLOW"
    
    q2 = engine.parse_query("રમેશે છેલ્લે ક્યારે ચૂકવ્યા?")
    assert q2["intent"] == "LAST_PAYMENT_DATE"
    
    q3 = engine.parse_query("આ અઠવાડિયે કેટલા લેવાના છે?")
    assert q3["intent"] == "WEEKLY_RECEIVABLES"
