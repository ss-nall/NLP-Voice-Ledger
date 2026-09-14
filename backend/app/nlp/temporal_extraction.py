"""
Temporal Expression Extraction & Normalization Module.
Parses Telugu & Gregorian calendar dates (సెప్టెంబర్ 17 కి, 17th Sept, repu, vache vaaram, Friday ki)
and computes standardized ISO-8601 timestamps relative to execution anchor.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from backend.app.nlp.telugu_lexicon import TEMPORAL_LEXICON, DAYS_OF_WEEK, TELUGU_MONTHS

class TemporalExtractor:
    """
    Extracts and normalizes temporal phrases into concrete dates.
    Accurately isolates dates so day numbers (e.g. 17 in సెప్టెంబర్ 17)
    are protected from amount extractors.
    """
    
    @staticmethod
    def extract_dates(text: str, anchor_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        if anchor_date is None:
            anchor_date = datetime.now()
            
        text_lower = text.lower()
        extracted = []
        
        # Check if sentence has future commitment or obligation markers
        has_due_intent = bool(re.search(
            r'\b(ivvali|ravali|kattali|istanu|isthanu|isthadu|annadu|baki|due|deadline|pay|by|'
            r'ఇవ్వాలి|రావాలి|కట్టాలి|ఇస్తాను|ఇస్తానన్నాడు|ఇస్తాడు|బాకీ|చెల్లించాలి|కడతాడు|చెల్లింపు)\b',
            text_lower
        ))
        
        # 1. Check relative keywords in TEMPORAL_LEXICON (e.g. repu, ninna, vache vaaram)
        for phrase, offset_days in TEMPORAL_LEXICON.items():
            pattern = r'(?:\b|\s+)' + re.escape(phrase) + r'(?:\s*(?:న|కి|కు|నాటికి|వరకు|roju|ki))?(?:\b|\s+|$|[.,!?])'
            for match in re.finditer(pattern, text_lower):
                target_date = anchor_date + timedelta(days=offset_days)
                matched_span = match.group(0).strip()
                is_due = (offset_days > 0) or any(k in matched_span for k in ["ki", "ku", "కి", "కు", "నాటికి", "వరకు"]) or has_due_intent
                role = "DUE_DATE" if is_due else "EVENT_DATE"
                extracted.append({
                    "raw_span": matched_span,
                    "start": match.start(),
                    "end": match.end(),
                    "normalized_date": target_date.strftime("%Y-%m-%d"),
                    "offset_days": offset_days,
                    "temporal_role": role,
                    "confidence": 0.96
                })
                
        # 2. Check Days of Week (e.g. "Friday ki", "సోమవారం కి", "next Monday")
        for day_name, target_weekday in DAYS_OF_WEEK.items():
            pattern = r'(?:\b|\s+)' + re.escape(day_name) + r'(?:\s*(?:న|కి|కు|నాటికి|వరకు|roju|ki))?(?:\b|\s+|$|[.,!?])'
            for match in re.finditer(pattern, text_lower):
                curr_weekday = anchor_date.weekday()
                days_ahead = (target_weekday - curr_weekday) % 7
                if days_ahead == 0:
                    days_ahead = 7
                target_date = anchor_date + timedelta(days=days_ahead)
                matched_span = match.group(0).strip()
                is_due = any(k in matched_span for k in ["ki", "ku", "కి", "కు", "నాటికి", "వరకు"]) or has_due_intent
                extracted.append({
                    "raw_span": matched_span,
                    "start": match.start(),
                    "end": match.end(),
                    "normalized_date": target_date.strftime("%Y-%m-%d"),
                    "offset_days": days_ahead,
                    "temporal_role": "DUE_DATE" if is_due else "EVENT_DATE",
                    "confidence": 0.94
                })
                
        # 3. Explicit Telugu & Gregorian Month + Day combinations
        # e.g. "సెప్టెంబర్ 17 కి", "సెప్టెంబరు 17వ తేదీ", "17 సెప్టెంబర్", "september 17th", "17th sep"
        for month_name, month_num in TELUGU_MONTHS.items():
            # Pattern A: [Month] [Day] (e.g. సెప్టెంబర్ 17 కి, september 17th)
            pat_a = r'(?:^|\s+)' + re.escape(month_name) + r'\s+(\d{1,2})(?:వ\s*తేదీ|వ\s*తేది|st|nd|rd|th)?(?:\s*(?:న|కి|కు|నాటికి|వరకు|roju|ki))?(?:\s+|$|[.,!?])'
            for match in re.finditer(pat_a, text_lower):
                try:
                    day = int(match.group(1))
                    if 1 <= day <= 31:
                        target_year = anchor_date.year
                        target_date = datetime(target_year, month_num, day)
                        if target_date.date() < anchor_date.date() and has_due_intent:
                            target_date = datetime(target_year + 1, month_num, day)
                        matched_span = match.group(0).strip()
                        is_due = any(k in matched_span for k in ["ki", "ku", "కి", "కు", "నాటికి", "వరకు"]) or has_due_intent
                        extracted.append({
                            "raw_span": matched_span,
                            "start": match.start(),
                            "end": match.end(),
                            "normalized_date": target_date.strftime("%Y-%m-%d"),
                            "offset_days": (target_date.date() - anchor_date.date()).days,
                            "temporal_role": "DUE_DATE" if is_due else "EVENT_DATE",
                            "confidence": 0.98
                        })
                except Exception:
                    pass

            # Pattern B: [Day] [Month] (e.g. 17 సెప్టెంబర్, 17th september)
            pat_b = r'(?:^|\s+)(\d{1,2})(?:వ\s*తేదీ|వ\s*తేది|st|nd|rd|th)?\s+' + re.escape(month_name) + r'(?:\s*(?:న|కి|కు|నాటికి|వరకు|roju|ki))?(?:\s+|$|[.,!?])'
            for match in re.finditer(pat_b, text_lower):
                try:
                    day = int(match.group(1))
                    if 1 <= day <= 31:
                        target_year = anchor_date.year
                        target_date = datetime(target_year, month_num, day)
                        if target_date.date() < anchor_date.date() and has_due_intent:
                            target_date = datetime(target_year + 1, month_num, day)
                        matched_span = match.group(0).strip()
                        is_due = any(k in matched_span for k in ["ki", "ku", "కి", "కు", "నాటికి", "వరకు"]) or has_due_intent
                        extracted.append({
                            "raw_span": matched_span,
                            "start": match.start(),
                            "end": match.end(),
                            "normalized_date": target_date.strftime("%Y-%m-%d"),
                            "offset_days": (target_date.date() - anchor_date.date()).days,
                            "temporal_role": "DUE_DATE" if is_due else "EVENT_DATE",
                            "confidence": 0.98
                        })
                except Exception:
                    pass

        # 4. Telugu standalone Day suffix: [Day]వ తేదీ / [Day]వ తేది (e.g. "17వ తేదీ కి", "5వ తేదీన")
        pat_day_only = r'(?:^|\s+)(\d{1,2})\s*(?:వ\s*తేదీ|వ\s*తేది)(?:\s*(?:న|కి|కు|నాటికి|వరకు))?(?:\s+|$|[.,!?])'
        for match in re.finditer(pat_day_only, text_lower):
            try:
                day = int(match.group(1))
                if 1 <= day <= 31:
                    target_year = anchor_date.year
                    target_month = anchor_date.month
                    target_date = datetime(target_year, target_month, day)
                    if target_date.date() < anchor_date.date() and has_due_intent:
                        target_month = (target_month % 12) + 1
                        target_year = target_year + (1 if target_month == 1 else 0)
                        target_date = datetime(target_year, target_month, day)
                    matched_span = match.group(0).strip()
                    is_due = any(k in matched_span for k in ["ki", "ku", "కి", "కు", "నాటికి", "వరకు"]) or has_due_intent
                    extracted.append({
                        "raw_span": matched_span,
                        "start": match.start(),
                        "end": match.end(),
                        "normalized_date": target_date.strftime("%Y-%m-%d"),
                        "offset_days": (target_date.date() - anchor_date.date()).days,
                        "temporal_role": "DUE_DATE" if is_due else "EVENT_DATE",
                        "confidence": 0.95
                    })
            except Exception:
                pass

        # 5. Numeric date patterns (e.g. "15-09-2026", "2026-09-15", "15/09/2026")
        numeric_patterns = [
            (r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b', "%d-%m-%Y"),
            (r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b', "%Y-%m-%d")
        ]
        for pat, fmt in numeric_patterns:
            for match in re.finditer(pat, text_lower):
                try:
                    matched_str = match.group(0)
                    normalized_match = matched_str.replace('/', '-')
                    target_date = datetime.strptime(normalized_match, fmt)
                    extracted.append({
                        "raw_span": matched_str,
                        "start": match.start(),
                        "end": match.end(),
                        "normalized_date": target_date.strftime("%Y-%m-%d"),
                        "offset_days": (target_date.date() - anchor_date.date()).days,
                        "temporal_role": "DUE_DATE" if has_due_intent else "EVENT_DATE",
                        "confidence": 0.98
                    })
                except Exception:
                    continue
                    
        # Sort by start index and deduplicate overlapping spans
        extracted = sorted(extracted, key=lambda x: x["start"])
        unique_extracted = []
        seen_spans = set()
        for item in extracted:
            span_key = (item["start"], item["end"])
            # Ensure no overlapping subsumed spans
            if not any(item["start"] >= s[0] and item["end"] <= s[1] for s in seen_spans):
                seen_spans.add(span_key)
                unique_extracted.append(item)
                
        return unique_extracted

# Global singleton
temporal_extractor = TemporalExtractor()
