import pytest
from backend.app.nlp.entity_extraction import entity_extractor
from backend.app.nlp.pipeline import nlp_pipeline

def test_expanded_actor_recognition():
    test_cases = [
        ("pavan ki 5000 ivaali next week", "Pavan"),
        ("5000 ivvali pavan ki", "Pavan"),
        ("suresh 5000 ichadu", "Suresh"),
        ("give 5000 to murthy", "Murthy"),
        ("kiran 2000 credit", "Kiran"),
        ("record 5000 for venkat", "Venkat"),
        ("paid 1000 to naresh", "Naresh"),
        ("5000 due from anil", "Anil"),
        ("subba rao ki 10000 ivvali", "Subba Rao"),
        ("raju 3000 ravali", "Raju"),
        ("5000 pavan", "Pavan"),
        ("pavan 5000", "Pavan"),
        ("kavya 3000 ichindi", "Kavya"),
        ("5000 transfer chesadu ramesh", "Ramesh"),
        ("chandu called 5000 istha annadu", "Chandu"),
        ("5000 ivvalasindi pavan", "Pavan"),
        ("పవన్ కి 5000 ఇవ్వాలి", "పవన్"),
        ("సురేష్ 2000 ఇచ్చాడు", "సురేష్"),
        ("వెంకట్ నుండి 3000 రావాలి", "వెంకట్"),
        ("లక్ష్మి ట్రేడర్స్ కి 10000 ఇవ్వాలి", "లక్ష్మి ట్రేడర్స్"),
        ("add customer kiran 2000", "Kiran"),
        ("need to pay 5000 to pavan", "Pavan"),
        ("pavan 5000 ivvali", "Pavan")
    ]
    
    for text, expected_actor in test_cases:
        res = entity_extractor.extract_entities(text)
        assert len(res["actors"]) > 0, f"Failed to extract actor from '{text}'"
        extracted_name = res["actors"][0]["name"]
        assert extracted_name.lower() == expected_actor.lower(), f"Expected '{expected_actor}' but got '{extracted_name}' for input '{text}'"

def test_pipeline_end_to_end_no_unspecified():
    queries = [
        "record 5000 for venkat",
        "pavan 5000 ivvali",
        "kavya 3000 ichindi",
        "give 5000 to murthy"
    ]
    for q in queries:
        res = nlp_pipeline.process_text(q, session_id="test_actor_sess")
        assert res.event.actor != "Unspecified", f"Pipeline returned Unspecified for query: '{q}'"
