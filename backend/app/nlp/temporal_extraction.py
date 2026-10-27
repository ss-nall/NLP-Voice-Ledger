"""
Multi-Lingual Temporal Expression Extraction & Normalization Module.
Parses Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, Gujarati & Gregorian calendar dates and computes standardized ISO-8601 timestamps.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from backend.app.nlp.indic_lexicon import (
    ALL_TEMPORAL_LEXICON, ALL_DAYS_OF_WEEK, ALL_MONTHS
)

POSTPOSITION_DUE_MARKERS = [
    "ki", "ku", "kku", "ukku", "ko", "ige", "ge", "kke", "inu", "lekku", "ne", "mate",
    "కి", "కు", "க்கு", "உக்கு", "को", "तक", "tak", "నాటికి", "வரை", "వరకు",
    "ಗೆ", "ಇಗೆ", "ಕ್ಕೆ", "ക്ക്", "ഇന്", "ലേക്ക്", "کو", "کے لیے", "ને", "માટે"
]

class TemporalExtractor:
    """
    Extracts and normalizes temporal phrases into concrete dates.
    Accurately isolates dates so day numbers (e.g. 17 in '17 सितंबर' or 'సెప్టెంబర్ 17')
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
            r'tharanum|varanum|kattanum|kodukkanum|tharen|sonnaan|sonnaaru|'
            r'dena|lena|dega|dunga|bola|wada|chahiye|'
            r'kodabeku|barabeku|kodtini|kodtane|'
            r'kodukkanam|tharanund|tharaam|paranju|'
            r'ada karna|wasool karna|wada kiya|'
            r'aapvana che|levana che|aapshe|vaado|'
            r'ఇవ్వాలి|రావాలి|కట్టాలి|ఇస్తాను|ఇస్తానన్నాడు|'
            r'தர வேண்டும்|வர வேண்டும்|கொடுக்க வேண்டும்|கட்ட வேண்டும்|சொன்னார்|'
            r'देना है|लेना है|देगा|दूंगा|बोला|बकाया|चुकाना|'
            r'ಕೊಡಬೇಕು|ಬರಬೇಕು|ಕೊಡುತ್ತೇನೆ|'
            r'കൊടുക്കണം|തരണം|തരാം|'
            r'دینا ہے|لینا ہے|دے گا|'
            r'આપવાના છે|લેવાના છે|આપશે)\b',
            text_lower
        ))
        
        # 1. Check relative keywords in ALL_TEMPORAL_LEXICON (e.g. repu, naalai, kal, aaj, vache vaaram, agle hafte, etc.)
        for phrase, offset_days in ALL_TEMPORAL_LEXICON.items():
            pattern = r'(?:\b|\s+)' + re.escape(phrase) + r'(?:\s*(?:న|కి|కు|నాటికి|వరకు|roju|ki|kku|ukku|க்கு|உக்கு|ko|se|को|से|tak|तक|ige|ge|kke|inu|lekku|ne|mate))?(?:\b|\s+|$|[.,!?])'
            for match in re.finditer(pattern, text_lower):
                effective_offset = offset_days
                if phrase in ["kal", "कल", "kale", "કાલે"]:
                    if any(v in text_lower for v in ["diya", "diye", "bheja", "aaya", "mila", "tha", "the", "दिया", "भेजा", "था", "aapya", "malya", "kotte", "thannu"]):
                        effective_offset = -1
                    else:
                        effective_offset = 1
                        
                target_date = anchor_date + timedelta(days=effective_offset)
                matched_span = match.group(0).strip()
                is_due = (effective_offset > 0) or any(k in matched_span for k in POSTPOSITION_DUE_MARKERS) or has_due_intent
                role = "DUE_DATE" if is_due else "EVENT_DATE"
                extracted.append({
                    "raw_span": matched_span,
                    "start": match.start(),
                    "end": match.end(),
                    "normalized_date": target_date.strftime("%Y-%m-%d"),
                    "offset_days": effective_offset,
                    "temporal_role": role,
                    "confidence": 0.96
                })
                
        # 2. Check Days of Week across 8 languages
        for day_name, target_weekday in ALL_DAYS_OF_WEEK.items():
            pattern = r'(?:\b|\s+)' + re.escape(day_name) + r'(?:\s*(?:న|కి|కు|kku|ukku|க்கு|உக்கு|ko|se|को|से|tak|तक|వరకు|roju|ki|ige|ge|kke|ne|mate))?(?:\b|\s+|$|[.,!?])'
            for match in re.finditer(pattern, text_lower):
                curr_weekday = anchor_date.weekday()
                days_ahead = (target_weekday - curr_weekday) % 7
                if days_ahead == 0:
                    days_ahead = 7
                target_date = anchor_date + timedelta(days=days_ahead)
                matched_span = match.group(0).strip()
                is_due = any(k in matched_span for k in POSTPOSITION_DUE_MARKERS) or has_due_intent or (days_ahead > 0)
                extracted.append({
                    "raw_span": matched_span,
                    "start": match.start(),
                    "end": match.end(),
                    "normalized_date": target_date.strftime("%Y-%m-%d"),
                    "offset_days": days_ahead,
                    "temporal_role": "DUE_DATE" if is_due else "EVENT_DATE",
                    "confidence": 0.94
                })
                
        # 3. Explicit Month + Day combinations across all 8 languages & Gregorian
        for month_name, month_num in ALL_MONTHS.items():
            # Pattern A: [Month] [Day]
            pat_a = r'(?:^|\s+)' + re.escape(month_name) + r'\s+(\d{1,2})(?:వ\s*తేదీ|వ\s*తేది|st|nd|rd|th|ஆம்\s*தேதி|તારીખ)?(?:\s*(?:న|కి|కు|kku|ukku|க்கு|உக்கு|ko|se|को|से|tak|तक|వరకు|roju|ki|ige|ge|kke|ne))?(?:\s+|$|[.,!?])'
            for match in re.finditer(pat_a, text_lower):
                try:
                    day = int(match.group(1))
                    if 1 <= day <= 31:
                        target_year = anchor_date.year
                        target_date = datetime(target_year, month_num, day)
                        if target_date.date() < anchor_date.date() and has_due_intent:
                            target_date = datetime(target_year + 1, month_num, day)
                        matched_span = match.group(0).strip()
                        offset_d = (target_date.date() - anchor_date.date()).days
                        is_due = any(k in matched_span for k in POSTPOSITION_DUE_MARKERS) or has_due_intent or (offset_d > 0)
                        extracted.append({
                            "raw_span": matched_span,
                            "start": match.start(),
                            "end": match.end(),
                            "normalized_date": target_date.strftime("%Y-%m-%d"),
                            "offset_days": offset_d,
                            "temporal_role": "DUE_DATE" if is_due else "EVENT_DATE",
                            "confidence": 0.98
                        })
                except Exception:
                    pass

            # Pattern B: [Day] [Month]
            pat_b = r'(?:^|\s+)(\d{1,2})(?:st|nd|rd|th|వ|ஆம்|મી|મી\s*તારીખ)?\s+' + re.escape(month_name) + r'(?:\s*(?:న|కి|కు|kku|ukku|க்கு|உக்கு|ko|se|को|से|tak|तक|వరకు|roju|ki|ige|ge|kke|ne))?(?:\s+|$|[.,!?])'
            for match in re.finditer(pat_b, text_lower):
                try:
                    day = int(match.group(1))
                    if 1 <= day <= 31:
                        target_year = anchor_date.year
                        target_date = datetime(target_year, month_num, day)
                        if target_date.date() < anchor_date.date() and has_due_intent:
                            target_date = datetime(target_year + 1, month_num, day)
                        matched_span = match.group(0).strip()
                        offset_d = (target_date.date() - anchor_date.date()).days
                        is_due = any(k in matched_span for k in POSTPOSITION_DUE_MARKERS) or has_due_intent or (offset_d > 0)
                        extracted.append({
                            "raw_span": matched_span,
                            "start": match.start(),
                            "end": match.end(),
                            "normalized_date": target_date.strftime("%Y-%m-%d"),
                            "offset_days": offset_d,
                            "temporal_role": "DUE_DATE" if is_due else "EVENT_DATE",
                            "confidence": 0.98
                        })
                except Exception:
                    pass

        # De-duplicate overlapping spans
        deduped = []
        for item in sorted(extracted, key=lambda x: (x["start"], -x["end"])):
            if not any(d["start"] <= item["start"] and d["end"] >= item["end"] for d in deduped):
                deduped.append(item)
                
        return deduped

# Global singleton
temporal_extractor = TemporalExtractor()
