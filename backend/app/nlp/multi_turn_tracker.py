"""
Multi-Turn Dialogue Context & Coreference Tracking Engine.
Maintains session state across conversational turns, resolves omitted subjects,
and tracks ongoing financial entities and transaction lifecycle context.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

class DialogueTurn:
    def __init__(self, raw_text: str, event: Optional[Dict[str, Any]], parsed_state: Dict[str, Any]):
        self.raw_text = raw_text
        self.event = event
        self.parsed_state = parsed_state
        self.timestamp = datetime.now()

class MultiTurnTracker:
    """
    Manages session-level conversational context and coreference resolution.
    """
    
    def __init__(self):
        # In-memory session store {session_id: [DialogueTurn]}
        self.sessions: Dict[str, List[DialogueTurn]] = {}
        
    def get_session_history(self, session_id: str) -> List[DialogueTurn]:
        return self.sessions.get(session_id, [])
        
    def add_turn(self, session_id: str, raw_text: str, event: Optional[Dict[str, Any]], parsed_state: Dict[str, Any]):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(DialogueTurn(raw_text, event, parsed_state))
        
    def resolve_coreference(self, session_id: str, current_entities: Dict[str, Any], current_text: str) -> Dict[str, Any]:
        """
        If current turn omits the actor or refers to 'remaining' amount,
        resolves these references from previous turns in the session.
        """
        history = self.get_session_history(session_id)
        actors = current_entities.get("actors", [])
        amounts = current_entities.get("amounts", [])
        text_lower = current_text.lower()
        
        resolved_actor = None
        resolved_from_context = False
        
        # 1. Coreference for Actor
        if actors:
            resolved_actor = actors[0]["name"]
        else:
            # Actor is omitted in this turn (e.g., '2000 ichadu' or 'Friday ki istanu annadu')
            # Look backwards through session history for most recent active entity
            for turn in reversed(history):
                if turn.event and turn.event.get("actor") and turn.event.get("actor") != "Unspecified":
                    resolved_actor = turn.event["actor"]
                    resolved_from_context = True
                    break
                    
        # 2. Check for contextual amount references like 'remaining', 'migilindi', 'balance'
        is_remaining_query = any(k in text_lower for k in ["remaining", "migilindi", "baki", "balance"])
        
        return {
            "resolved_actor": resolved_actor if resolved_actor else "Unspecified",
            "actor_resolved_from_context": resolved_from_context,
            "is_remaining_referenced": is_remaining_query,
            "turn_depth": len(history) + 1
        }
        
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

# Global singleton
multi_turn_tracker = MultiTurnTracker()
