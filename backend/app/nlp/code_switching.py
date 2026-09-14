"""
Code-Switching Detection & Index (CMI) Calculator.
Identifies code-switch boundary points, matrix language vs embedded language,
and computes the Code-Switching Index (CMI).
"""

from typing import Dict, Any, List
from backend.app.nlp.language_detection import language_identifier

class CodeSwitchDetector:
    """
    Computes linguistic code-switching statistics and marks switch boundaries.
    """
    
    @staticmethod
    def analyze(text: str) -> Dict[str, Any]:
        lang_result = language_identifier.identify(text)
        token_tags = lang_result["token_tags"]
        
        if not token_tags:
            return {
                "cmi_score": 0.0,
                "switch_points": [],
                "matrix_language": "unknown",
                "embedded_languages": [],
                "segmented_spans": []
            }
            
        # Detect switch points (where adjacent non-numeric tokens differ in language)
        switch_points = []
        valid_tokens = [t for t in token_tags if t["language"] not in ["numeric", "punctuation"]]
        
        for i in range(1, len(valid_tokens)):
            prev_lang = valid_tokens[i - 1]["language"]
            curr_lang = valid_tokens[i]["language"]
            if prev_lang != curr_lang:
                switch_points.append({
                    "index": i,
                    "from_token": valid_tokens[i - 1]["token"],
                    "from_lang": prev_lang,
                    "to_token": valid_tokens[i]["token"],
                    "to_lang": curr_lang
                })
                
        # Calculate CMI (Code-Switching Index)
        n = len(valid_tokens)
        if n == 0:
            cmi = 0.0
            matrix_lang = "numeric"
            embedded_langs = []
        else:
            lang_counts: Dict[str, int] = {}
            for t in valid_tokens:
                l = t["language"]
                lang_counts[l] = lang_counts.get(l, 0) + 1
                
            sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
            matrix_lang = sorted_langs[0][0]
            embedded_langs = [l[0] for l in sorted_langs[1:]]
            max_wi = sorted_langs[0][1]
            p = len(switch_points)
            
            # CMI formula: (N - max(wi) + P) / (2 * N) normalized to [0, 1]
            cmi = (n - max_wi + p) / max(2.0 * n, 1.0)
            cmi = min(max(cmi, 0.0), 1.0)
            
        # Group tokens into contiguous language segments
        segmented_spans = []
        if token_tags:
            current_lang = token_tags[0]["language"]
            current_tokens = [token_tags[0]["token"]]
            
            for t in token_tags[1:]:
                if t["language"] == current_lang:
                    current_tokens.append(t["token"])
                else:
                    segmented_spans.append({
                        "language": current_lang,
                        "text": " ".join(current_tokens)
                    })
                    current_lang = t["language"]
                    current_tokens = [t["token"]]
            if current_tokens:
                segmented_spans.append({
                    "language": current_lang,
                    "text": " ".join(current_tokens)
                })
                
        return {
            "cmi_score": round(cmi, 3),
            "switch_points_count": len(switch_points),
            "switch_points": switch_points,
            "matrix_language": matrix_lang,
            "embedded_languages": embedded_langs,
            "segmented_spans": segmented_spans
        }

# Global singleton
code_switch_detector = CodeSwitchDetector()
