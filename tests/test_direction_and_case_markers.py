"""
Cross-Lingual Direction & Case Marker Disambiguation Test Suite.
Verifies Paid vs Received (Realized Cash Flow) and Payable vs Receivable (Pending Obligations)
across Hindi, Urdu, Telugu, Tamil, Kannada, Malayalam, Gujarati, and English.
"""

import pytest
from backend.app.nlp.pipeline import nlp_pipeline

def test_hindi_paid_vs_received_and_obligations():
    # 1. Received: Pawan gave 20,000 to business (Inflow / Receivable reduction)
    res1 = nlp_pipeline.process_text("पवन ने 20000 दिया है", session_id="test_hi_dir_1")
    assert res1.event.direction == "receivable"
    assert res1.event.amount == 20000
    assert res1.event.event_type == "partial_payment"
    assert "पवन" in res1.event.actor or "Pawan" in res1.event.actor

    # 2. Paid: Business gave 10,000 to Pawan (Outflow / Payable reduction)
    res2 = nlp_pipeline.process_text("पवन को 10000 दिया है", session_id="test_hi_dir_2")
    assert res2.event.direction == "payable"
    assert res2.event.amount == 10000
    assert res2.event.event_type in ["payment_made", "partial_payment"]

    # 3. Receivable: Business has to collect 5,000 from Pawan (Pending Inflow)
    res3 = nlp_pipeline.process_text("पवन से 5000 लेना है", session_id="test_hi_dir_3")
    assert res3.event.direction == "receivable"
    assert res3.event.amount == 5000
    assert res3.event.event_type == "receivable_invoice"

    # 4. Payable: Business has to pay 8,000 to Pawan (Pending Outflow)
    res4 = nlp_pipeline.process_text("पवन को 8000 देना है", session_id="test_hi_dir_4")
    assert res4.event.direction == "payable"
    assert res4.event.amount == 8000
    assert res4.event.event_type == "payable_obligation"


def test_telugu_paid_vs_received_and_obligations():
    # 1. Received: Pawan gave 20,000 (3rd person past: ichadu)
    res1 = nlp_pipeline.process_text("పవన్ 20000 ఇచ్చాడు", session_id="test_te_dir_1")
    assert res1.event.direction == "receivable"
    assert res1.event.amount == 20000

    # 2. Paid: Business gave 10,000 to Pawan (1st person past: ichanu)
    res2 = nlp_pipeline.process_text("పవన్ కి 10000 ఇచ్చాను", session_id="test_te_dir_2")
    assert res2.event.direction == "payable"
    assert res2.event.amount == 10000

    # 3. Receivable: Have to collect from Pawan (Ablative + ravali)
    res3 = nlp_pipeline.process_text("పవన్ నుంచి 5000 రావాలి", session_id="test_te_dir_3")
    assert res3.event.direction == "receivable"
    assert res3.event.amount == 5000

    # 4. Payable: Have to pay to Pawan (Dative + ivvali)
    res4 = nlp_pipeline.process_text("పవన్ కి 8000 ఇవ్వాలి", session_id="test_te_dir_4")
    assert res4.event.direction == "payable"
    assert res4.event.amount == 8000


def test_tamil_paid_vs_received_and_obligations():
    # 1. Received: Pawan gave 20,000 (3rd person: koduthaar)
    res1 = nlp_pipeline.process_text("பவன் 20000 கொடுத்தார்", session_id="test_ta_dir_1")
    assert res1.event.direction == "receivable"
    assert res1.event.amount == 20000

    # 2. Paid: Business gave 10,000 to Pawan (1st person: koduthen)
    res2 = nlp_pipeline.process_text("பவனுக்கு 10000 கொடுத்தேன்", session_id="test_ta_dir_2")
    assert res2.event.direction == "payable"
    assert res2.event.amount == 10000

    # 3. Receivable: Have to collect from Pawan (irundhu vara vendum)
    res3 = nlp_pipeline.process_text("பவனிடம் இருந்து 5000 வர வேண்டும்", session_id="test_ta_dir_3")
    assert res3.event.direction == "receivable"
    assert res3.event.amount == 5000

    # 4. Payable: Have to pay to Pawan (kku kodukka vendum)
    res4 = nlp_pipeline.process_text("பவனுக்கு 8000 கொடுக்க வேண்டும்", session_id="test_ta_dir_4")
    assert res4.event.direction == "payable"
    assert res4.event.amount == 8000


def test_kannada_paid_vs_received_and_obligations():
    # 1. Received: Pawan gave 20,000 (3rd person: kottiddane)
    res1 = nlp_pipeline.process_text("ಪವನ್ 20000 ಕೊಟ್ಟಿದ್ದಾನೆ", session_id="test_kn_dir_1")
    assert res1.event.direction == "receivable"
    assert res1.event.amount == 20000

    # 2. Paid: Business gave 10,000 to Pawan (1st person: kotte)
    res2 = nlp_pipeline.process_text("ಪವನ್ ಗೆ 10000 ಕೊಟ್ಟೆ", session_id="test_kn_dir_2")
    assert res2.event.direction == "payable"
    assert res2.event.amount == 10000

    # 3. Receivable: Have to collect from Pawan (inda barabeku)
    res3 = nlp_pipeline.process_text("ಪವನ್ ಇಂದ 5000 ಬರಬೇಕು", session_id="test_kn_dir_3")
    assert res3.event.direction == "receivable"
    assert res3.event.amount == 5000

    # 4. Payable: Have to pay to Pawan (ge kodabeku)
    res4 = nlp_pipeline.process_text("ಪವನ್ ಗೆ 8000 ಕೊಡಬೇಕು", session_id="test_kn_dir_4")
    assert res4.event.direction == "payable"
    assert res4.event.amount == 8000


def test_malayalam_paid_vs_received_and_obligations():
    # 1. Received: Pawan gave 20,000 (thannu)
    res1 = nlp_pipeline.process_text("പവൻ 20000 തന്നു", session_id="test_ml_dir_1")
    assert res1.event.direction == "receivable"
    assert res1.event.amount == 20000

    # 2. Paid: Business gave 10,000 to Pawan (koduthu)
    res2 = nlp_pipeline.process_text("പവന് 10000 കൊടുത്തു", session_id="test_ml_dir_2")
    assert res2.event.direction == "payable"
    assert res2.event.amount == 10000

    # 3. Receivable: Have to collect from Pawan (ninnu kittanundu)
    res3 = nlp_pipeline.process_text("പവനിൽ നിന്ന് 5000 കിട്ടാനുണ്ട്", session_id="test_ml_dir_3")
    assert res3.event.direction == "receivable"
    assert res3.event.amount == 5000

    # 4. Payable: Have to pay to Pawan (nu kodukkanundu)
    res4 = nlp_pipeline.process_text("പവന് 8000 കൊടുക്കാനുണ്ട്", session_id="test_ml_dir_4")
    assert res4.event.direction == "payable"
    assert res4.event.amount == 8000


def test_gujarati_paid_vs_received_and_obligations():
    # 1. Received: Pawan gave 20,000 (3rd person: aapya)
    res1 = nlp_pipeline.process_text("પવને 20000 આપ્યા", session_id="test_gu_dir_1")
    assert res1.event.direction == "receivable"
    assert res1.event.amount == 20000

    # 2. Paid: Business gave 10,000 to Pawan (me ... aapya)
    res2 = nlp_pipeline.process_text("મેં પવનને 10000 આપ્યા", session_id="test_gu_dir_2")
    assert res2.event.direction == "payable"
    assert res2.event.amount == 10000

    # 3. Receivable: Have to collect from Pawan (pasethi levana che)
    res3 = nlp_pipeline.process_text("પવન પાસેથી 5000 લેવાના છે", session_id="test_gu_dir_3")
    assert res3.event.direction == "receivable"
    assert res3.event.amount == 5000

    # 4. Payable: Have to pay to Pawan (ne aapvana che)
    res4 = nlp_pipeline.process_text("પવનને 8000 આપવાના છે", session_id="test_gu_dir_4")
    assert res4.event.direction == "payable"
    assert res4.event.amount == 8000


def test_urdu_paid_vs_received_and_obligations():
    # 1. Received: Pawan gave 20,000 (ne diya)
    res1 = nlp_pipeline.process_text("پون نے 20000 دیا", session_id="test_ur_dir_1")
    assert res1.event.direction == "receivable"
    assert res1.event.amount == 20000

    # 2. Paid: Business gave 10,000 to Pawan (maine ... diya)
    res2 = nlp_pipeline.process_text("میں نے پون کو 10000 دیا", session_id="test_ur_dir_2")
    assert res2.event.direction == "payable"
    assert res2.event.amount == 10000

    # 3. Receivable: Have to collect from Pawan (se lena hai)
    res3 = nlp_pipeline.process_text("پون سے 5000 لینا ہے", session_id="test_ur_dir_3")
    assert res3.event.direction == "receivable"
    assert res3.event.amount == 5000

    # 4. Payable: Have to pay to Pawan (ko dena hai)
    res4 = nlp_pipeline.process_text("پون کو 8000 دینا ہے", session_id="test_ur_dir_4")
    assert res4.event.direction == "payable"
    assert res4.event.amount == 8000


def test_english_paid_vs_received_and_obligations():
    # 1. Received: Pawan gave 20,000
    res1 = nlp_pipeline.process_text("Pawan gave 20000", session_id="test_en_dir_1")
    assert res1.event.direction == "receivable"
    assert res1.event.amount == 20000

    # 2. Paid: Paid 10,000 to Pawan
    res2 = nlp_pipeline.process_text("Paid 10000 to Pawan", session_id="test_en_dir_2")
    assert res2.event.direction == "payable"
    assert res2.event.amount == 10000

    # 3. Receivable: To collect 5,000 from Pawan
    res3 = nlp_pipeline.process_text("Collect 5000 from Pawan", session_id="test_en_dir_3")
    assert res3.event.direction == "receivable"
    assert res3.event.amount == 5000

    # 4. Payable: To pay 8,000 to Pawan
    res4 = nlp_pipeline.process_text("Pay 8000 to Pawan", session_id="test_en_dir_4")
    assert res4.event.direction == "payable"
    assert res4.event.amount == 8000
