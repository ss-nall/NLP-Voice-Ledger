"""
Speech Processing & Spoken Telugu Numeral Parsing Engine.
Converts spoken audio and voice transcripts with Telugu/English code-mixed spoken numerals
into normalized numerical values, extracted entities, and speech synthesis responses.
"""

import re
import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from backend.app.nlp.telugu_lexicon import TELUGU_NUMERALS, TEMPORAL_LEXICON, DIRECTION_MARKERS, PAYMENT_METHODS

class TeluguSpokenNumberParser:
    """
    Decodes complex spoken Indic/Telugu numerals and mixed phrases into exact integers.
    Examples:
      - 'aidhu vandalu' -> 500
      - 'rendu vela five hundred' -> 2500
      - 'nalabhai vela' -> 40000
      - 'oka laksha yaabhai vela' -> 150000
      - 'mudu vela rendu vandala yaabhai' -> 3250
    """
    
    @staticmethod
    def parse_spoken_number(text: str) -> Optional[int]:
        # Tokenize while preserving comma-separated digits, decimals, and metric suffixes (e.g. 50,000, 1,50,000.50, 25k)
        tokens = re.findall(r'\d{1,3}(?:,\d{2,3})+(?:\.\d+)?k?|\d+(?:\.\d+)?k?|[a-zA-Z0-9\u0C00-\u0C7F]+', text.lower())
        if not tokens:
            return None
            
        total = 0.0
        current_multiplier_group = 0.0
        has_num = False
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check if formatted digit with commas (e.g. 50,000 or 1,50,000 or 50,000.50)
            if ',' in token and re.match(r'^\d{1,3}(?:,\d{2,3})+(?:\.\d+)?k?$', token):
                clean_t = token.replace(',', '')
                if clean_t.endswith('k'):
                    val = float(clean_t[:-1]) * 1000.0
                else:
                    val = float(clean_t)
                current_multiplier_group += val
                has_num = True
                i += 1
                continue

            # Check if direct digit with 'k' suffix (e.g. '5k', '25k', '1.5k')
            k_match = re.match(r'^(\d+(?:\.\d+)?)\s*k$', token)
            if k_match:
                val = float(k_match.group(1)) * 1000.0
                total += current_multiplier_group + val
                current_multiplier_group = 0.0
                has_num = True
                i += 1
                continue

            # Check if direct digit or decimal
            if token.isdigit() or re.match(r'^\d+\.\d+$', token):
                current_multiplier_group += float(token)
                has_num = True
                i += 1
                continue
                
            # Check Telugu / Indian accent number word
            if token in TELUGU_NUMERALS:
                val = float(TELUGU_NUMERALS[token])
                has_num = True
                
                # Fused large numbers (e.g. padivela=10000, iravaivela=20000, పదివేలు=10000, etc.)
                if val >= 1000 and val not in [1000.0, 100000.0, 10000000.0]:
                    total += current_multiplier_group + val
                    current_multiplier_group = 0.0
                elif val in [100000.0, 10000000.0]: # Lakh or Crore
                    if current_multiplier_group == 0.0:
                        current_multiplier_group = 1.0
                    total += current_multiplier_group * val
                    current_multiplier_group = 0.0
                elif val == 1000.0: # Thousand / Vela / Thouzad / Thoujand
                    if current_multiplier_group == 0.0:
                        current_multiplier_group = 1.0
                    total += current_multiplier_group * val
                    current_multiplier_group = 0.0
                elif val == 100.0: # Hundred / Vanda / Hunderd
                    if current_multiplier_group == 0.0:
                        current_multiplier_group = 1.0
                    current_multiplier_group = current_multiplier_group * val
                else:
                    # Units or Tens
                    current_multiplier_group += val
                    
            i += 1
            
        total += current_multiplier_group
        if has_num and total > 0:
            return int(total) if total.is_integer() else round(total, 2)
        return None

    @classmethod
    def replace_spoken_numbers_in_text(cls, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Scans text for sequences of spoken numbers and replaces them with standard digits
        while returning exact span mappings. Pre-processes Telugu sandhi.
        """
        from backend.app.nlp.transliteration import split_telugu_sandhi
        text = split_telugu_sandhi(text)
        words = text.split()
        extracted_amounts = []
        
        # Look for multi-word spoken number segments
        # e.g., 'aidhu vandalu', 'rendu vela 500', 'nalabhai vela', '5 thouzad', '50,000'
        i = 0
        new_words = []
        
        while i < len(words):
            # Check windows from 6 down to 1
            matched = False
            for window_size in range(6, 0, -1):
                if i + window_size <= len(words):
                    segment = " ".join(words[i:i+window_size])
                    # Tokenize while preserving formatted comma digits
                    seg_tokens = re.findall(r'\d{1,3}(?:,\d{2,3})+(?:\.\d+)?k?|\d+(?:\.\d+)?k?|[a-zA-Z0-9\u0C00-\u0C7F]+', segment.lower())
                    is_num_seq = bool(seg_tokens) and all(
                        t.replace(',', '').replace('.', '', 1).isdigit() or
                        t in TELUGU_NUMERALS or
                        bool(re.match(r'^\d+(?:\.\d+)?k$', t.replace(',', '')))
                        for t in seg_tokens
                    )
                    
                    if is_num_seq and len(seg_tokens) > 0:
                        amount = cls.parse_spoken_number(segment)
                        if amount is not None and amount > 0:
                            new_words.append(str(amount))
                            extracted_amounts.append({
                                "raw_spoken_text": segment,
                                "parsed_amount": amount,
                                "start_idx": i,
                                "end_idx": i + window_size
                            })
                            i += window_size
                            matched = True
                            break
            if not matched:
                new_words.append(words[i])
                i += 1
                
        return " ".join(new_words), extracted_amounts


class SpeechProcessor:
    """
    Handles speech audio ingestion, simulated acoustic waveforms,
    speech recognition transcription, and Telugu spoken phrase extraction.
    """
    
    def __init__(self):
        self.num_parser = TeluguSpokenNumberParser()
        
    def process_spoken_transcript(self, raw_transcript: str, audio_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Takes raw transcribed audio text and normalizes spoken numbers, dialect idioms,
        and generates audio pipeline diagnostics.
        """
        normalized_text, spoken_amounts = self.num_parser.replace_spoken_numbers_in_text(raw_transcript)
        
        # Calculate phonetic/audio confidence estimate
        # Simulated acoustic clarity metric (or real if supplied via audio_metadata)
        confidence = 0.95
        if "confidence" in (audio_metadata or {}):
            confidence = float(audio_metadata["confidence"])
            
        # Generate simulated audio waveform data points for UI visualizer
        waveform = self._generate_waveform_points(len(raw_transcript))
        
        # Generate bilingual TTS response string
        spoken_response_te, spoken_response_en = self._generate_tts_confirmation(normalized_text, spoken_amounts)
        
        return {
            "raw_spoken_transcript": raw_transcript,
            "normalized_transcript": normalized_text,
            "spoken_amounts": spoken_amounts,
            "audio_confidence": confidence,
            "waveform_data": waveform,
            "tts_response": {
                "telugu": spoken_response_te,
                "english": spoken_response_en
            },
            "timestamp": datetime.now().isoformat()
        }
        
    def _generate_waveform_points(self, length: int) -> List[float]:
        """Generates realistic normalized audio frequency/amplitude bars for UI visualizer."""
        num_points = min(max(length * 2, 32), 64)
        points = []
        for i in range(num_points):
            val = (math.sin(i * 0.35) * 0.4 + math.cos(i * 0.15) * 0.3 + 0.5)
            val = max(0.1, min(val, 0.95))
            points.append(round(val, 2))
        return points
        
    def _generate_tts_confirmation(self, normalized_text: str, spoken_amounts: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Creates natural spoken feedback for voice response."""
        amount_str = str(spoken_amounts[0]["parsed_amount"]) if spoken_amounts else "amount"
        
        if "ivvali" in normalized_text.lower():
            te = f"₹{amount_str} చెల్లింపు రికార్డ్ చేశాము."
            en = f"Recorded ₹{amount_str} payment due."
        elif "ichadu" in normalized_text.lower() or "ichesa" in normalized_text.lower():
            te = f"₹{amount_str} చెల్లింపు అందింది అని అప్‌డేట్ చేశాము."
            en = f"Recorded ₹{amount_str} payment received."
        else:
            te = f"వివరాలు విజయవంతంగా రికార్డ్ చేశాము."
            en = f"Transaction details recorded successfully."
            
        return te, en

# Global singleton
speech_processor = SpeechProcessor()
