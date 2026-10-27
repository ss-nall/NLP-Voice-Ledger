"""
Compound Utterance Clause Splitter for Multi-Transaction Spoken Utterances ("One-Breath" Ingestion).
Decomposes compound sentences across English, Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, Gujarati
into discrete, atomic transaction clauses while strictly protecting numeric commas (15,000).
"""

import re
from typing import List, Dict, Any

COORDINATING_CONJUNCTIONS = [
    # Telugu
    r'(?:\b|\s)మరియు(?:\b|\s)',
    r'(?:\b|\s)అలాగే(?:\b|\s)',
    r'(?:\b|\s)తో పాటు(?:\b|\s)',
    r'(?:\b|\s)అదే విధంగా(?:\b|\s)',
    r'\bmariyu\b',
    r'\balage\b',
    # Tamil
    r'(?:\b|\s)மற்றும்(?:\b|\s)',
    r'(?:\b|\s)அதேபோல்(?:\b|\s)',
    r'(?:\b|\s)கூடவே(?:\b|\s)',
    r'\bmattrum\b',
    r'\bkoodave\b',
    r'\badhepol\b',
    # Hindi
    r'(?:\b|\s)और(?:\b|\s)',
    r'(?:\b|\s)तथा(?:\b|\s)',
    r'(?:\b|\s)साथ ही(?:\b|\s)',
    r'\baur\b',
    r'\btatha\b',
    r'\bsaath hi\b',
    # Kannada
    r'(?:\b|\s)ಮತ್ತು(?:\b|\s)',
    r'(?:\b|\s)ಹಾಗೂ(?:\b|\s)',
    r'(?:\b|\s)ಜೊತೆಗೆ(?:\b|\s)',
    r'\bmattu\b',
    r'\bhaagu\b',
    r'\bjothege\b',
    # Malayalam
    r'(?:\b|\s)കൂടാതെ(?:\b|\s)',
    r'(?:\b|\s)ഒപ്പം(?:\b|\s)',
    r'(?:\b|\s)പിന്നെ(?:\b|\s)',
    r'\bkoodathe\b',
    r'\boppam\b',
    r'\bpinne\b',
    # Urdu
    r'(?:\b|\s)اور(?:\b|\s)',
    r'(?:\b|\s)نیز(?:\b|\s)',
    r'(?:\b|\s)پھر(?:\b|\s)',
    r'\baur\b',
    r'\bphir\b',
    # Gujarati
    r'(?:\b|\s)અને(?:\b|\s)',
    r'(?:\b|\s)તેમજ(?:\b|\s)',
    r'(?:\b|\s)સાથે(?:\b|\s)',
    r'\bane\b',
    r'\btemaj\b',
    r'\bsathe\b',
    # English
    r'\band\b',
    r'\balso\b',
    r'\bplus\b',
    # Comma followed by a verbal action or payment (e.g., "Paid 2000 to Ramesh, received 1500...")
    r',\s*(?=(?:paid|received|need to|gave|collected|kotte|thannu|diya|ichanu|aapya|koduthu|[a-zA-Z\u0C00-\u0C7F\u0B80-\u0BFF\u0900-\u097F\u0C80-\u0CFF\u0D00-\u0D7F\u0600-\u06FF\u0A80-\u0AFF]+\s+(?:ki|ku|ko|se|ige|kku|ne|inda|nundi)))'
]

class CompoundClauseSplitter:
    """
    Decomposes multi-intent compound sentences into atomic clauses.
    """

    def split_clauses(self, text: str) -> List[Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return []

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
