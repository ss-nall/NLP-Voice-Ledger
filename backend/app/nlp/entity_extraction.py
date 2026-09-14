"""
Financial Named Entity Recognition (NER) Module.
Extracts ACTOR, BUSINESS, AMOUNT, CURRENCY, PAYMENT_METHOD, PRODUCT, STATUS, and INVOICE.
Combines rule-based grammar patterns, lexicon matching, and token position heuristics.
"""

import re
from typing import Dict, Any, List, Optional
from backend.app.nlp.telugu_lexicon import (
    TELUGU_HONORIFICS, PAYMENT_METHODS, BUSINESS_TERMS, TELUGU_NUMERALS
)
from backend.app.nlp.speech_processor import TeluguSpokenNumberParser

KNOWN_BUSINESS_KEYWORDS = {
    "traders", "enterprises", "stores", "kirana", "electricals", "hardware", "agency",
    "distributors", "mills", "wholesalers", "medicals", "cloths", "shop", "mart",
    "fertilizers", "automobiles", "services", "general", "supermarket", "jewellers",
    "textiles", "bakery", "hotel", "restaurant", "stationery", "trading", "industries",
    "ట్రేడర్స్", "స్టోర్స్", "కిరాణా", "ఎంటర్‌ప్రైజెస్", "ఏజెన్సీ", "టెక్స్‌టైల్స్"
}

EXCLUDED_ACTOR_WORDS = {
    # Days of the week
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "somavaram", "mangalavaram", "budhavaram", "guruvaram", "sukravaram", "sanivaram", "adivaram",
    "సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం", "ఆదివారం",
    # Temporal keywords
    "yesterday", "today", "tomorrow", "ninna", "monna", "eroju", "ee roju", "nedu", "repu", "ellundi", "yelundi",
    "next", "last", "this", "vache", "vacche", "poyina", "kritham", "vaaram", "varam", "week", "nela", "month", "year",
    "morning", "evening", "night", "sayantram", "udayam", "madyanam", "afternoon", "daily",
    "నిన్న", "మొన్న", "ఈరోజు", "రేపు", "ఎల్లుండి", "వచ్చే", "వారం", "నెల", "సంవత్సరం",
    # Numbers & Spoken numerals
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "hundred", "thousand", "lakh", "crore",
    "okati", "rendu", "mudu", "moodu", "nalugu", "aidhu", "ayidu", "aaru", "yedu", "edu", "enimidi", "thommidi", "tommidi", "padi", "padhi",
    "vanda", "vandalu", "vandala", "nooru", "veyyi", "vela", "velu", "renduvela", "mooduvela", "naaluguvela", "aiduvela", "padivela", "iravaivela",
    "laksha", "lakshalu", "koti", "kotlu", "k",
    "ఒకటి", "ఒక", "రెండు", "మూడు", "నాలుగు", "ఐదు", "ఆరు", "ఏడు", "ఎనిమిది", "తొమ్మిది", "పది", "పదకొండు", "పన్నెండు",
    "ఇరవై", "ముప్పై", "నలభై", "యాభై", "అరవై", "డెబ్బై", "ఎనభై", "తొంభై",
    "వంద", "వందలు", "వందల", "నూరు", "ఇన్నూరు", "మున్నూరు", "నానూరు", "ఐనూరు",
    "వేయి", "వెయ్యి", "వేలు", "వేల", "రెండువేలు", "రెండువేల", "మూడువేలు", "మూడువేల", "నాలుగువేలు", "నాలుగువేల",
    "ఐదువేలు", "ఐదువేల", "ఆరువేలు", "ఆరువేల", "ఏడువేలు", "ఏడువేల", "ఎనిమిదివేలు", "ఎనిమిదివేల", "తొమ్మిదివేలు", "తొమ్మిదివేల",
    "పదివేలు", "పదివేల", "పదిహేనువేలు", "పదిహేనువేల", "ఇరవైవేలు", "ఇరవైవేల", "ముప్పైవేలు", "ముప్పైవేల", "నలభైవేలు", "నలభైవేల",
    "యాభైవేలు", "యాభైవేల", "అరవైవేలు", "అరవైవేల", "డెబ్బైవేలు", "డెబ్బైవేల", "ఎనభైవేలు", "ఎనభైవేల", "తొంభైవేలు", "తొంభైవేల",
    "లక్ష", "లక్షలు", "లక్షల", "రెండు లక్షలు", "రెండు లక్షల", "కోటి", "కోట్లు", "కోట్ల",
    # Financial transaction terms
    "cash", "credit", "debit", "online", "gpay", "phonepe", "paytm", "upi", "cheque", "bank",
    "transfer", "account", "balance", "total", "amount", "money", "rupees", "rs", "inr", "dabbulu", "rupayalu", "chillara",
    "remaining", "baki", "pending", "advance", "udhari", "discount", "bill", "invoice", "inv",
    "payment", "due", "refund", "interest", "saraku", "maal", "saman", "goods", "stock", "khata",
    "already", "direct", "directly", "settled", "done", "complete", "completed", "full", "pura",
    "ఖాతా", "బాకీ", "రూపాయలు", "అడ్వాన్స్", "నగదు", "చెల్లింపు",
    # Verbs & Verb forms
    "ivvali", "ivaali", "ivali", "ivvaali", "evali", "evvali", "eeyali", "chellinchali", "kattali", "kattalsindi", "kattaali", "ivvalasindi", "ivvalsindi",
    "ravali", "raavali", "ravalsi", "ravalsindi", "teesukovali", "teeskovali", "theeskovali", "vasool", "vasul", "collect", "ravanundi", "vachindi", "vachindhi", "vachayi", "vacchesindi", "vacchindi", "andindi", "cherindi",
    "ichadu", "ichindi", "icharu", "ichanu", "icha", "ichesadu", "ichesa", "ichesanu", "icheysadu", "ichesthadu", "ichestha", "ichaanu", "ichesindi", "ichessaru",
    "pampadu", "pampindi", "pamparu", "pampanu", "pampa", "pampaadu", "pampinchadu", "pampesadu", "pampesa",
    "kattadu", "kattindi", "kattaru", "kattanu", "katta", "kattesa", "kattesanu", "kattesadu", "kattesindi", "kattesaru",
    "chellinchadu", "chellincha", "chellinchanu", "chellincharu", "chellinchindi", "chellinchesadu",
    "chesadu", "chesindi", "chesaru", "chesanu", "chesa", "annadu", "cheppadu", "istanu", "istha", "isthadu", "isthanannadu", "isthannadu",
    "give", "pay", "paid", "receive", "received", "sent", "send", "take", "took", "need", "have", "must", "will", "owes", "owe", "collected", "bought", "sold", "transferred",
    "record", "add", "create", "note", "entry", "book", "show", "view", "get", "check", "update", "clear", "list", "settle", "motham",
    "customer", "supplier", "dealer", "vendor",
    "ఇవ్వాలి", "రావాలి", "ఇచ్చాడు", "ఇచ్చింది", "ఇచ్చారు", "ఇచ్చేశాడు", "ఇచ్చేసాడు", "ఇచ్చేశారు", "ఇచ్చేసింది",
    "చెల్లించాలి", "చెల్లించాడు", "చెల్లించింది", "చెల్లించారు", "చెల్లించేశాడు", "చెల్లించేశారు",
    "కట్టాలి", "కట్టాడు", "కట్టింది", "కట్టారు", "కట్టేసా", "కట్టేశాను", "కట్టేశాడు", "కట్టేసాడు", "కట్టేశారు", "కట్టేసింది",
    "వచ్చింది", "వచ్చాయి", "అందింది", "చేరింది", "తీసుకోవాలి", "వసూలు", "కలెక్ట్", "డ్యూ",
    "పంపాము", "పంపాను", "పంపాం", "పంపాడు", "పంపింది", "పంపారు", "పంపించేశాడు",
    "అన్నాడు", "చెప్పాడు", "ట్రాన్స్ఫర్", "పే", "సెటిల్", "క్లియర్", "మొత్తం",
    # Prepositions & Postpositions & Particles
    "ki", "ku", "kante", "nundi", "nunchi", "daggara", "daggarnundi", "vadda", "tho", "to", "from", "for", "in", "on", "at", "by", "with", "of", "into",
    "ga", "ani", "undhi", "undi", "unna", "unnayi", "unnam", "kadha", "ra", "andi", "gurinchi", "meeda", "lo",
    "కి", "కు", "నుండి", "నుంచి", "దగ్గర", "వద్ద", "తో", "లో", "గారికి", "అన్నకి",
    # Pronouns & Possessives
    "nenu", "naaku", "naku", "na", "naa", "memu", "maaku", "maku", "ma", "maa",
    "nuvvu", "neeku", "ne", "nee", "meeru", "meeku", "mee", "vaadu", "vaadiki", "atanu", "athanu", "athaniki",
    "aame", "aameku", "aameki", "vaallu", "vaallaki", "vaaru", "vaariki", "evaru", "evariki", "tanu", "aayana", "aavida",
    "i", "me", "he", "she", "him", "her", "us", "they", "them",
    "నాకు", "మాకు", "నా", "మా", "నీకు", "మీకు", "వారికి", "వీరికి", "వాడికి", "ఆమెకు", "ఆమెకి", "అతనికి", "మనకు", "తనకు",
    "అతను", "ఆమె", "ఆయన", "వాడు", "వారు", "వాళ్ళు", "ఆవిడ", "తాను",
    # Telugu & Gregorian Months
    "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్", "మే", "జూన్", "జూలై", "ఆగస్టు", "ఆగష్టు", "సెప్టెంబర్", "సెప్టెంబరు", "అక్టోబర్", "అక్టోబరు", "నవంబర్", "నవంబరు", "డిసెంబర్", "డిసెంబరు",
    "తేదీ", "తేది", "రోజు"
}

def _clean_actor_candidate(cand: str) -> str:
    tokens = [re.sub(r'[^\w\u0C00-\u0C7F]', '', t) for t in cand.split()]
    tokens = [t for t in tokens if t]
    valid = []
    for t in tokens:
        tl = t.lower()
        # Strip trailing postpositions if attached
        for suffix in ["gariki", "annaki", "bhaiki", "sethki", "ki", "ku", "nundi", "nunchi", "గారికి", "అన్నకి", "కి", "కు", "నుండి", "నుంచి"]:
            if tl.endswith(suffix) and len(tl) > len(suffix) + 2:
                t = t[:-len(suffix)]
                tl = t.lower()
                break
        if (tl in KNOWN_BUSINESS_KEYWORDS or (tl not in EXCLUDED_ACTOR_WORDS and tl not in TELUGU_NUMERALS)) \
           and not re.match(r'^\d+(\.\d+)?(k|thousand|thouzad|thoujand|thouzand|lakh|lakha|crore|koti)?$', tl):
            valid.append(t)
            
    if not valid:
        return ""
    name = " ".join(valid)
    return name.title() if not name.isupper() else name


class FinancialEntityExtractor:
    """
    Extracts structured financial slot entities from code-mixed sentences.
    Applies Date-First Masking to prevent dates from colliding with monetary amounts.
    """
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, Any]:
        from backend.app.nlp.temporal_extraction import TemporalExtractor
        text_lower = text.lower()
        entities = {
            "actors": [],
            "amounts": [],
            "payment_methods": [],
            "products": [],
            "statuses": [],
            "invoices": []
        }
        
        # 0. Date-First Extraction & Masking for Amount Extractor
        temporal_spans = TemporalExtractor.extract_dates(text)
        masked_chars = list(text)
        for ts in temporal_spans:
            s_idx = max(0, ts["start"])
            e_idx = min(len(masked_chars), ts["end"])
            for k in range(s_idx, e_idx):
                masked_chars[k] = " "
        text_masked_for_amounts = "".join(masked_chars)
        text_masked_lower = text_masked_for_amounts.lower()
        
        # 1. Extract Amounts (Digits, Symbols, or Spoken Numerals from masked text)
        amount_patterns = [
            r'(?:rs\.?|inr|₹)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(k|thousand|thouzad|thoujand|thouzand|thousend|vela|veye|lakh|lacs|lac|lakha|laksha|లక్ష|crore|crores|krore|koti|కోటి)?\b',
        ]
        
        found_amounts = []
        for pat in amount_patterns:
            for match in re.finditer(pat, text_masked_lower):
                raw_val = match.group(1).replace(',', '')
                try:
                    val = float(raw_val)
                    if val > 0:
                        matched_full = match.group(0).strip()
                        if any(s in matched_full for s in ["k", "thousand", "thouzad", "thoujand", "thouzand", "thousend", "vela", "veye"]):
                            val *= 1000
                        elif any(s in matched_full for s in ["lakh", "lacs", "lac", "lakha", "laksha", "లక్ష"]):
                            val *= 100000
                        elif any(s in matched_full for s in ["crore", "crores", "krore", "koti", "కోటి"]):
                            val *= 10000000
                        found_amounts.append({
                            "value": int(val) if isinstance(val, float) and val.is_integer() else (int(val) if isinstance(val, int) else round(val, 2)),
                            "currency": "INR",
                            "raw_span": match.group(0).strip(),
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.98
                        })
                except ValueError:
                    continue
                    
        # Check spoken numbers (e.g. 'aidhu vandalu', 'rendu vela 500', 'padi velu', 'iravai velu')
        _, spoken_amounts = TeluguSpokenNumberParser.replace_spoken_numbers_in_text(text_masked_for_amounts)
        for sa in spoken_amounts:
            val = sa["parsed_amount"]
            if not any(a["value"] == val for a in found_amounts):
                found_amounts.append({
                    "value": val,
                    "currency": "INR",
                    "raw_span": sa["raw_spoken_text"],
                    "start": sa["start_idx"],
                    "end": sa["end_idx"],
                    "confidence": 0.95
                })
                
        entities["amounts"] = found_amounts
        
        # 2. Extract Actors / Counterparties
        def add_actor(raw_name: str, raw_span: str, atype="PERSON", conf=0.95):
            clean = _clean_actor_candidate(raw_name)
            if clean and clean.lower() not in EXCLUDED_ACTOR_WORDS and clean.lower() not in TELUGU_NUMERALS:
                is_biz = any(k in clean.lower() for k in KNOWN_BUSINESS_KEYWORDS) or atype == "BUSINESS"
                if not any(a["name"].lower() == clean.lower() for a in entities["actors"]):
                    entities["actors"].append({
                        "name": clean,
                        "raw_span": raw_span,
                        "type": "BUSINESS" if is_biz else "PERSON",
                        "confidence": conf
                    })

        # Strategy 0: Direct Subject Inflow/Outflow (e.g. 'Pavan naku 500 ichadu', 'Pavan 500 ichadu', 'రమేష్ నాకు 500 ఇచ్చాడు', 'సాత్విక్ నాకు 2500 ఇచ్చాడు')
        subj_inflow_pat = r'(?:^|\s+)([a-zA-Z\u0C00-\u0C7F]+(?:\s+[a-zA-Z\u0C00-\u0C7F]+)?)\s+(?:naaku|naku|maaku|maku|to me|to us|నాకు|మాకు)?\s*(?:rs\.?|inr|₹)?\s*(?:\d+(?:,\d+)*(?:\.\d+)?|[a-zA-Z\u0C00-\u0C7F\s]+?)\s*(?:ichadu|ichindi|icharu|ichesadu|kattadu|pampadu|pampesadu|chellinchadu|chellincharu|paid|transferred|sent|ఇచ్చాడు|ఇచ్చింది|కట్టాడు|చెల్లించాడు)(?:\s+|$|[.,!?])'
        for m in re.finditer(subj_inflow_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.98)

        # Strategy A: Multi-word Business Names (e.g. 'Sri Lakshmi Traders', 'Balaji Kirana', 'లక్ష్మి ట్రేడర్స్')
        biz_pat = r'(?:^|\s+)([a-zA-Z\u0C00-\u0C7F]+(?:\s+[a-zA-Z\u0C00-\u0C7F]+){0,2}\s+(?:traders|enterprises|stores|kirana|electricals|hardware|agency|distributors|mills|wholesalers|medicals|shop|mart|jewellers|textiles|supermarket|automobiles|fertilizers|ట్రేడర్స్|స్టోర్స్|కిరాణా|ఎంటర్‌ప్రైజెస్))(?:\s+|$|[.,!?])'
        for m in re.finditer(biz_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), atype="BUSINESS", conf=0.97)

        # Strategy B: Postpositional cues (Telugu / Romanized markers)
        postpos_pat = r'(?:^|\s+)([a-zA-Z\u0C00-\u0C7F]+(?:\s+[a-zA-Z\u0C00-\u0C7F]+){0,2})\s+(?:gariki|annaki|bhaiki|sethki|ki|ku|nundi|nunchi|daggarnundi|daggara\s+nundi|daggara|vadda\s+nundi|vadda|tho|గారికి|అన్నకి|కి|కు|నుండి|నుంచి|దగ్గర\s+నుండి|దగ్గర్నుండి|దగ్గర|వద్ద\s+నుండి|వద్ద|తో)(?:\s+|$|[.,!?])'
        for m in re.finditer(postpos_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.96)

        # Strategy C: Prepositional cues & Action commands
        prep_pat = r'(?:^|\s+)(?:to|from|for|by|pay|give|paid to|transferred to|received from|due to|due from|payable to|receivable from|account of|record|add customer|add supplier)\s+([a-zA-Z\u0C00-\u0C7F]+(?:\s+[a-zA-Z\u0C00-\u0C7F]+){0,2})(?:\s+|$|[.,!?])'
        for m in re.finditer(prep_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.95)

        # Strategy D: Honorifics (e.g. 'Pavan Anna', 'Ramesh Garu', 'Sharma Seth')
        honorific_pat = r'(?:^|\s+)([a-zA-Z\u0C00-\u0C7F]+(?:\s+[a-zA-Z\u0C00-\u0C7F]+){0,1})\s+(?:garu|anna|gaaru|bhai|ji|seth|reddy|rao|saab|babu|annaya|ayya|amma|గారు|అన్న|సేథ్|రావు|రెడ్డి)(?:\s+|$|[.,!?])'
        for m in re.finditer(honorific_pat, text, re.IGNORECASE):
            add_actor(m.group(0), m.group(0), conf=0.95)

        # Strategy E: Action Verbs following/preceding Name
        verb_pat_pre = r'(?:^|\s+)([a-zA-Z\u0C00-\u0C7F]+)\s+(?:ichadu|ichindi|icharu|pampadu|pampindi|kattadu|chesadu|annadu|ఇచ్చాడు|ఇచ్చింది|పంపాడు|కట్టాడు)(?:\s+|$|[.,!?])'
        for m in re.finditer(verb_pat_pre, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.94)

        verb_pat_post = r'\b(?:transfer chesadu|ichesadu|ichadu|pampadu|ivvalasindi|ivvalsindi|ivvali|ravali|kattalsindi|kattadu)\s+(?:to|for)?\s*([a-zA-Z\u0C00-\u0C7F]+)\b'
        for m in re.finditer(verb_pat_post, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.93)

        # Strategy F: Fallback Positional Subject / Object / Noun
        if not entities["actors"]:
            tokens = [re.sub(r'[^\w\u0C00-\u0C7F]', '', t) for t in text.split()]
            tokens = [t for t in tokens if t]
            candidates = [t for t in tokens if t.lower() not in EXCLUDED_ACTOR_WORDS and t.lower() not in TELUGU_NUMERALS and not re.match(r'^\d+(\.\d+)?(k|lakh)?$', t.lower())]
            if candidates:
                cand_name = candidates[0]
                add_actor(cand_name, cand_name, conf=0.90)

        # 3. Extract Payment Method
        for method_type, keywords in PAYMENT_METHODS.items():
            for kw in keywords:
                if re.search(r'(?:^|\s+)' + re.escape(kw) + r'(?:\s+|$|[.,!?])', text_lower):
                    entities["payment_methods"].append({"method": method_type, "confidence": 0.95})
                    break

        # 4. Extract Invoices
        inv_match = re.search(r'\b(?:inv|bill|invoice)\s*#?\s*([a-zA-Z0-9_-]+)\b', text, re.IGNORECASE)
        if inv_match:
            entities["invoices"].append({"invoice_number": inv_match.group(1)})

        return entities

# Global singleton
entity_extractor = FinancialEntityExtractor()
