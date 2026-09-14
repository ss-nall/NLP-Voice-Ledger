import pytest
from backend.app.nlp.speech_processor import TeluguSpokenNumberParser, speech_processor

def test_single_spoken_numerals():
    assert TeluguSpokenNumberParser.parse_spoken_number("aidhu vandalu") == 500
    assert TeluguSpokenNumberParser.parse_spoken_number("rendu vela") == 2000
    assert TeluguSpokenNumberParser.parse_spoken_number("mudu vela") == 3000
    assert TeluguSpokenNumberParser.parse_spoken_number("nalabhai vela") == 40000
    assert TeluguSpokenNumberParser.parse_spoken_number("oka laksha") == 100000
    assert TeluguSpokenNumberParser.parse_spoken_number("padhi vela") == 10000
    assert TeluguSpokenNumberParser.parse_spoken_number("రెండువేల") == 2000
    assert TeluguSpokenNumberParser.parse_spoken_number("మూడువేల") == 3000
    assert TeluguSpokenNumberParser.parse_spoken_number("ఐదువేల") == 5000

def test_compound_code_mixed_numerals():
    # 'rendu vela five hundred' -> 2500
    assert TeluguSpokenNumberParser.parse_spoken_number("rendu vela five hundred") == 2500
    assert TeluguSpokenNumberParser.parse_spoken_number("aidhu vela 500") == 5500
    assert TeluguSpokenNumberParser.parse_spoken_number("రెండువేల 500") == 2500
    assert TeluguSpokenNumberParser.parse_spoken_number("ఐదువేల 200") == 5200
    assert TeluguSpokenNumberParser.parse_spoken_number("3 వేల 700") == 3700
    assert TeluguSpokenNumberParser.parse_spoken_number("లక్ష యాభై వేలు") == 150000
    assert TeluguSpokenNumberParser.parse_spoken_number("లక్ష యాభై వేల 500") == 150500

def test_spoken_transcript_replacement():
    raw = "Ramesh Aidhu vandalu ivvali vache vaaram"
    norm_text, amounts = TeluguSpokenNumberParser.replace_spoken_numbers_in_text(raw)
    assert "500" in norm_text
    assert len(amounts) > 0
    assert amounts[0]["parsed_amount"] == 500

    raw_sathwik = "సాత్విక్ నాకు రెండువేల 500 ఇచ్చాడు."
    norm_sathwik, amounts_sathwik = TeluguSpokenNumberParser.replace_spoken_numbers_in_text(raw_sathwik)
    assert "2500" in norm_sathwik
    assert amounts_sathwik[0]["parsed_amount"] == 2500

def test_speech_processor_pipeline():
    res = speech_processor.process_spoken_transcript("Ramesh Aidhu vandalu ivvali vache vaaram")
    assert "500" in res["normalized_transcript"]
    assert len(res["waveform_data"]) > 0
    assert res["audio_confidence"] > 0.90
    assert "₹500" in res["tts_response"]["english"] or "Recorded" in res["tts_response"]["english"]

def test_indian_accent_pronunciations():
    # Test thousand phonetic variants
    assert TeluguSpokenNumberParser.parse_spoken_number("5 thouzad") == 5000
    assert TeluguSpokenNumberParser.parse_spoken_number("5 thoujand") == 5000
    assert TeluguSpokenNumberParser.parse_spoken_number("rendu thouzand") == 2000
    assert TeluguSpokenNumberParser.parse_spoken_number("10 taujand") == 10000
    assert TeluguSpokenNumberParser.parse_spoken_number("twenty five thouzad") == 25000
    assert TeluguSpokenNumberParser.parse_spoken_number("five thouzad five hunderd") == 5500
    assert TeluguSpokenNumberParser.parse_spoken_number("oka lakha yaabhai thouzad") == 150000
    assert TeluguSpokenNumberParser.parse_spoken_number("25k") == 25000
    assert TeluguSpokenNumberParser.parse_spoken_number("5k") == 5000

    # Test spoken transcript replacements
    raw = "Customer 5 thouzad ivvali repu"
    norm_text, amounts = TeluguSpokenNumberParser.replace_spoken_numbers_in_text(raw)
    assert "5000" in norm_text
    assert amounts[0]["parsed_amount"] == 5000

    raw2 = "Supplier ki 10 thoujand pay chesa"
    norm_text2, amounts2 = TeluguSpokenNumberParser.replace_spoken_numbers_in_text(raw2)
    assert "10000" in norm_text2
    assert amounts2[0]["parsed_amount"] == 10000

def test_tens_and_thousands_spoken_numerals():
    # Padi velu, iravai velu, muppai velu, etc.
    assert TeluguSpokenNumberParser.parse_spoken_number("padi velu") == 10000
    assert TeluguSpokenNumberParser.parse_spoken_number("padhi velu") == 10000
    assert TeluguSpokenNumberParser.parse_spoken_number("పది వేలు") == 10000
    assert TeluguSpokenNumberParser.parse_spoken_number("iravai velu") == 20000
    assert TeluguSpokenNumberParser.parse_spoken_number("iravai vela") == 20000
    assert TeluguSpokenNumberParser.parse_spoken_number("ఇరవై వేలు") == 20000
    assert TeluguSpokenNumberParser.parse_spoken_number("muppai velu") == 30000
    assert TeluguSpokenNumberParser.parse_spoken_number("nalabhai velu") == 40000
    assert TeluguSpokenNumberParser.parse_spoken_number("yaabhai velu") == 50000
    assert TeluguSpokenNumberParser.parse_spoken_number("aravai velu") == 60000
    assert TeluguSpokenNumberParser.parse_spoken_number("debbai velu") == 70000
    assert TeluguSpokenNumberParser.parse_spoken_number("enabhai velu") == 80000
    assert TeluguSpokenNumberParser.parse_spoken_number("thombhai velu") == 90000
    assert TeluguSpokenNumberParser.parse_spoken_number("iravai aidhu velu") == 25000
    assert TeluguSpokenNumberParser.parse_spoken_number("oka laksha yaabhai velu") == 150000

def test_actor_name_pronoun_isolation():
    from backend.app.nlp.entity_extraction import FinancialEntityExtractor
    from backend.app.nlp.transliteration import get_bilingual_names
    
    # "pavan naku 500 ichadu" -> Actor MUST be "Pavan" (NOT "Pavan Na")
    res1 = FinancialEntityExtractor.extract_entities("pavan naku 500 ichadu")
    assert len(res1["actors"]) > 0
    assert res1["actors"][0]["name"] == "Pavan"
    assert res1["amounts"][0]["value"] == 500

    # Telugu script equivalent: "పవన్ నాకు 500 ఇచ్చాడు"
    res2 = FinancialEntityExtractor.extract_entities("పవన్ నాకు 500 ఇచ్చాడు")
    assert len(res2["actors"]) > 0
    assert res2["actors"][0]["name"] == "పవన్"

    # Telugu compound: "సాత్విక్ నాకు రెండువేల 500 ఇచ్చాడు"
    from backend.app.nlp.pipeline import nlp_pipeline
    pipe_res = nlp_pipeline.process_text("సాత్విక్ నాకు రెండువేల 500 ఇచ్చాడు.")
    assert pipe_res.event.actor == "సాత్విక్ (Sathwik)" or "సాత్విక్" in pipe_res.event.actor
    assert pipe_res.event.amount == 2500.0
    assert pipe_res.event.direction == "receivable"

    # Bilingual Name resolution (Telugu input puts English translation in brackets)
    bi1 = get_bilingual_names("Pavan")
    assert bi1["english"] == "Pavan"
    assert bi1["telugu"] == "పవన్"
    assert bi1["display"] == "Pavan (పవన్)"
    
    bi2 = get_bilingual_names("పవన్")
    assert bi2["english"] == "Pavan"
    assert bi2["telugu"] == "పవన్"
    assert bi2["display"] == "పవన్ (Pavan)"

def test_deepak_and_sathvik_sandhi_and_bilingual_names():
    from backend.app.nlp.transliteration import get_bilingual_names, split_telugu_sandhi
    from backend.app.database.session import SessionLocal
    from backend.app.services.conversation_service import conversation_service
    from backend.app.api.endpoints.ledger import reset_all_ledger_data
    
    # 1. Bilingual formatting with English in brackets for Telugu names
    bi_deepak = get_bilingual_names("దీపక్")
    assert bi_deepak["english"] == "Deepak"
    assert bi_deepak["telugu"] == "దీపక్"
    assert bi_deepak["display"] == "దీపక్ (Deepak)"

    bi_sathvik = get_bilingual_names("సాత్విక్")
    assert bi_sathvik["english"] == "Sathvik"
    assert bi_sathvik["telugu"] == "సాత్విక్"
    assert bi_sathvik["display"] == "సాత్విక్ (Sathvik)"

    # 2. Sandhi splitting: పదివేలిచ్చాడు -> పదివేలు ఇచ్చాడు
    sandhi_res = split_telugu_sandhi("దీపక్ నాకు పదివేలిచ్చాడు.")
    assert "పదివేలు" in sandhi_res
    assert "ఇచ్చాడు" in sandhi_res

    # 3. Full End-to-End Database Transaction for "సాత్విక్ నాకు రెండువేల 500 ఇచ్చాడు." (Must be 2500, Actor: Sathwik)
    db = SessionLocal()
    reset_all_ledger_data(db)

    res_sathvik = conversation_service.process_message(db, "సాత్విక్ నాకు రెండువేల 500 ఇచ్చాడు.", session_id="test_sathvik_sess")
    assert res_sathvik["success"] is True
    assert res_sathvik["ledger_update"]["amount"] == 2500.0
    assert res_sathvik["ledger_update"]["direction"] == "receivable"
    assert res_sathvik["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert "సాత్విక్" in res_sathvik["ledger_update"]["actor_display"]

    # 4. Full End-to-End Database Transaction for "దీపక్ నాకు పదివేలిచ్చాడు." (Must be 10000, NOT 0)
    res_deepak = conversation_service.process_message(db, "దీపక్ నాకు పదివేలిచ్చాడు.", session_id="test_deepak_sess")
    assert res_deepak["success"] is True
    assert res_deepak["ledger_update"]["amount"] == 10000.0
    assert res_deepak["ledger_update"]["direction"] == "receivable"
    assert res_deepak["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert "దీపక్" in res_deepak["ledger_update"]["actor_display"]

    reset_all_ledger_data(db)
    db.close()

def test_phonetic_entity_disambiguation():
    from backend.app.nlp.entity_resolution import EntityResolver
    
    known = [
        {"id": 1, "name": "సాత్విక్ (Sathwik)", "aliases": ["Sathwik", "Satvik"], "type": "customer", "balance": 1500.0},
        {"id": 2, "name": "రమేష్ (Ramesh)", "aliases": ["Ramesh", "Rameshbabu"], "type": "customer", "balance": 3000.0}
    ]
    
    # Exact match should NOT require disambiguation
    exact_res = EntityResolver.resolve_entity("Sathwik", known)
    assert exact_res["matched"] is True
    assert exact_res["requires_disambiguation"] is False

    # Close phonetic match "Satvika" vs "Sathwik" should trigger disambiguation
    fuzzy_res = EntityResolver.resolve_entity("Satvika", known)
    assert fuzzy_res["requires_disambiguation"] is True
    assert len(fuzzy_res["suggested_matches"]) > 0
    assert fuzzy_res["suggested_matches"][0]["id"] == 1
