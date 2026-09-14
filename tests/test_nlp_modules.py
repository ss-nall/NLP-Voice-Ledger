import pytest
from backend.app.nlp.language_detection import language_identifier
from backend.app.nlp.code_switching import code_switch_detector
from backend.app.nlp.transliteration import phonetic_normalizer, indic_phonetic_fingerprint
from backend.app.nlp.temporal_extraction import temporal_extractor
from backend.app.nlp.entity_extraction import entity_extractor
from backend.app.nlp.relation_extraction import relation_extractor

def test_language_identification():
    # Romanized code-mixed
    res1 = language_identifier.identify("Ramesh ki 2500 pending undi")
    assert res1["is_code_mixed"] is True
    
    # Telugu script
    res2 = language_identifier.identify("రమేష్ కి 2500 పెండింగ్ ఉంది")
    assert res2["primary_language"] in ["telugu_script", "code_mixed_script"]

def test_code_switching_cmi():
    res = code_switch_detector.analyze("Ramesh ki 2500 pending undi")
    assert res["cmi_score"] >= 0.0
    assert len(res["segmented_spans"]) > 0

def test_transliteration_normalization():
    res = phonetic_normalizer.normalize("Ramesh ki 2500 ivvaali ra")
    assert "ivvali" in res["normalized_text"]
    
    # Indic phonetic fingerprint
    assert indic_phonetic_fingerprint("Ramesh") == indic_phonetic_fingerprint("Rameshu")

def test_temporal_extraction():
    res = temporal_extractor.extract_dates("Ramesh ninna 2000 ichadu")
    assert len(res) > 0
    assert res[0]["raw_span"] == "ninna"
    assert res[0]["offset_days"] == -1
    assert res[0]["temporal_role"] == "EVENT_DATE"
    
    res_due = temporal_extractor.extract_dates("Ramesh Friday ki remaining istanu annadu")
    assert len(res_due) > 0
    assert "friday" in res_due[0]["raw_span"].lower()
    assert res_due[0]["temporal_role"] == "DUE_DATE"

def test_entity_and_relation_direction():
    # Direction test 1: 'Supplier ki 8000 ivvali' -> Payable
    text1 = "Supplier ki 8000 ivvali"
    ents1 = entity_extractor.extract_entities(text1)
    rel1 = relation_extractor.extract_relation(text1, ents1)
    assert rel1["direction"] == "payable"
    assert ents1["amounts"][0]["value"] == 8000
    
    # Direction test 2: 'Ramesh nundi 2500 ravali' -> Receivable
    text2 = "Ramesh nundi 2500 ravali"
    ents2 = entity_extractor.extract_entities(text2)
    rel2 = relation_extractor.extract_relation(text2, ents2)
    assert rel2["direction"] == "receivable"
    assert ents2["amounts"][0]["value"] == 2500

    # Direction test 3: User's reported case 'pavan ki 5000 ivaali next week'
    text3 = "pavan ki 5000 ivaali next week"
    ents3 = entity_extractor.extract_entities(text3)
    assert len(ents3["actors"]) > 0
    assert ents3["actors"][0]["name"] == "Pavan"
    assert ents3["amounts"][0]["value"] == 5000
    rel3 = relation_extractor.extract_relation(text3, ents3)
    assert rel3["direction"] == "payable"
    dates3 = temporal_extractor.extract_dates(text3)
    assert len(dates3) > 0
    assert dates3[0]["temporal_role"] == "DUE_DATE"

    # Direction test 4: English preposition 'pay 4000 to chandu tomorrow'
    text4 = "pay 4000 to chandu tomorrow"
    ents4 = entity_extractor.extract_entities(text4)
    assert any(a["name"] == "Chandu" for a in ents4["actors"])
    assert ents4["amounts"][0]["value"] == 4000
    rel4 = relation_extractor.extract_relation(text4, ents4)
    assert rel4["direction"] == "payable"
