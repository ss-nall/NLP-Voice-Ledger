"""
Comprehensive Enterprise NLP Benchmark & Golden Evaluation Test Suite.
Verifies blackboard pipeline execution, compound clause splitting, Indic phonetic resolution,
multi-turn DST pronoun coreference, and semantic financial queries.
"""

import pytest
import time
from backend.app.nlp.pipeline import nlp_pipeline
from backend.app.nlp.clause_splitter import clause_splitter
from backend.app.nlp.indic_phonetics import indic_phonetic_matcher, strip_indic_honorifics
from backend.app.nlp.dialogue_tracker import dialogue_tracker
from backend.app.nlp.query_engine import query_engine

def test_blackboard_pipeline_telemetry():
    """Ensure pipeline produces telemetry spans and structured blackboard result."""
    text = "రమేష్ కి 5000 ఇచ్చాను"
    t0 = time.perf_counter()
    res = nlp_pipeline.process_text(text)
    latency_ms = (time.perf_counter() - t0) * 1000

    assert res.event.actor == "రమేష్"
    assert res.event.amount == 5000.0
    assert res.event.direction == "payable"
    assert len(res.telemetry) > 0
    assert latency_ms < 100.0  # High-performance pipeline latency

def test_compound_clause_splitting():
    """Verify multi-transaction compound sentences decompose into discrete events."""
    compound_text = "రమేష్ కి 2000 ఇచ్చాను అలాగే సురేష్ 500 ఇచ్చాడు"
    clauses = clause_splitter.split_clauses(compound_text)
    
    assert len(clauses) == 2
    assert clauses[0]["is_compound"] is True
    assert "రమేష్" in clauses[0]["clause_text"]
    assert "సురేష్" in clauses[1]["clause_text"]

    # Process through pipeline
    res = nlp_pipeline.process_text(compound_text)
    assert len(res.all_events) == 2
    assert res.all_events[0].amount == 2000.0
    assert res.all_events[1].amount == 500.0

def test_indic_phonetic_matcher():
    """Verify Indic phonetic similarity across spelling variants and honorifics."""
    # Suffix stripping
    assert strip_indic_honorifics("రమేష్ గారికి") == "రమేష్"
    assert strip_indic_honorifics("Pavan garu") == "Pavan"
    assert strip_indic_honorifics("Sathwik anna") == "Sathwik"

    # Phonetic matching
    score1 = indic_phonetic_matcher.match_score("Sathwik", "Satvik")
    assert score1 >= 0.85

    score2 = indic_phonetic_matcher.match_score("Pawan", "Pavan")
    assert score2 >= 0.85

    score3 = indic_phonetic_matcher.match_score("రమేశ్", "రమేష్")
    assert score3 >= 0.85

def test_multi_turn_dst_pronoun_anaphora():
    """Verify dialogue state tracker resolves pronouns to the active entity."""
    session_id = f"test_sess_{int(time.time())}"
    
    # Turn 1: Establish entity
    res1 = nlp_pipeline.process_text("రమేష్ కి 1000 ఇచ్చాను", session_id=session_id)
    assert res1.event.actor == "రమేష్"

    # Turn 2: Pronoun reference ('అతను 500 ఇచ్చాడు')
    res2 = nlp_pipeline.process_text("అతను 500 ఇచ్చాడు", session_id=session_id)
    assert res2.event.actor == "రమేష్"
    assert res2.event.amount == 500.0
    assert res2.event.direction == "receivable"

def test_semantic_query_parsing():
    """Verify analytical queries parse correctly."""
    q1 = query_engine.parse_query("ఎవరు ఎక్కువ బాకీ ఇవ్వాలి?")
    assert q1["is_query"] is True
    assert q1["intent"] == "TOP_DEBTORS"

    q2 = query_engine.parse_query("ఈ వారం మొత్తం రావాల్సిన బాకీలు ఎంత?")
    assert q2["is_query"] is True
    assert q2["intent"] == "TOTAL_RECEIVABLES"
    assert q2["filters"].get("time_range") == "THIS_WEEK"
