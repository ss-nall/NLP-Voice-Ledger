import pytest
from backend.app.nlp.multi_turn_tracker import multi_turn_tracker
from backend.app.nlp.pipeline import nlp_pipeline

def test_multi_turn_coreference():
    session_id = "test_multi_turn_session"
    multi_turn_tracker.clear_session(session_id)
    
    # Turn 1: "Ramesh ki 5000 pending undi"
    res1 = nlp_pipeline.process_text("Ramesh ki 5000 pending undi", session_id=session_id)
    assert res1.event.actor == "Ramesh"
    assert res1.event.amount == 5000.0
    
    # Turn 2: "2000 ichadu" (Actor omitted)
    res2 = nlp_pipeline.process_text("2000 ichadu", session_id=session_id)
    assert res2.event.actor == "Ramesh"
    assert res2.event.amount == 2000.0
    assert res2.coreference_info["actor_resolved_from_context"] is True
    
    # Turn 3: "Remaining Friday ki istanu annadu" (Actor and amount contextually resolved)
    res3 = nlp_pipeline.process_text("Remaining Friday ki istanu annadu", session_id=session_id, current_balance=3000.0)
    assert res3.event.actor == "Ramesh"
    assert res3.event.amount == 3000.0
    assert res3.event.event_type == "payment_commitment"
