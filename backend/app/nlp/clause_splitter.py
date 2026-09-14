"""
Compound Utterance Clause Splitter for Multi-Transaction Spoken Utterances.
Decomposes compound sentences (e.g. 'రమేష్ కి 2000 ఇచ్చాను అలాగే సురేష్ 500 ఇచ్చాడు')
into discrete, atomic transaction clauses while strictly protecting numeric commas (15,000).
"""

import re
from typing import List, Dict, Any

COORDINATING_CONJUNCTIONS = [
    r'(?:\b|\s)మరియు(?:\b|\s)',
    r'(?:\b|\s)అలాగే(?:\b|\s)',
    r'(?:\b|\s)తో పాటు(?:\b|\s)',
    r'(?:\b|\s)అదే విధంగా(?:\b|\s)',
    r'\band\b',
    r'\balso\b',
    r'\bplus\b',
    r'\bmariyu\b',
    r'\balage\b'
]

class CompoundClauseSplitter:
    """
    Decomposes multi-intent compound sentences into atomic clauses.
    """

    def split_clauses(self, text: str) -> List[Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return []

        # Only split on explicit coordinating conjunctions
        regex_pattern = '|'.join(COORDINATING_CONJUNCTIONS)
        raw_splits = re.split(regex_pattern, cleaned, flags=re.IGNORECASE)

        clauses: List[str] = []
        for segment in raw_splits:
            seg = segment.strip().rstrip('.,;')
            if len(seg.split()) >= 2:
                clauses.append(seg)

        if len(clauses) > 1:
            return [
                {
                    "clause_index": idx,
                    "clause_text": c,
                    "is_compound": True,
                    "total_clauses": len(clauses)
                }
                for idx, c in enumerate(clauses)
            ]

        return [
            {
                "clause_index": 0,
                "clause_text": cleaned,
                "is_compound": False,
                "total_clauses": 1
            }
        ]

clause_splitter = CompoundClauseSplitter()
