"""
Multi-Lingual Financial Named Entity Recognition (NER) Module.
Extracts ACTOR, BUSINESS, AMOUNT, CURRENCY, PAYMENT_METHOD, PRODUCT, STATUS, and INVOICE
across 8 Indian Languages: English, Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, and Gujarati.
Combines rule-based grammar patterns, multi-lingual lexicon matching, and token position heuristics.
"""

import re
from typing import Dict, Any, List, Optional
from backend.app.nlp.indic_lexicon import (
    ALL_HONORIFICS, ALL_PAYMENT_METHODS, ALL_BUSINESS_TERMS, ALL_INDIC_NUMERALS
)
from backend.app.nlp.speech_processor import IndicSpokenNumberParser

# Unicode Character Range for 8 Languages
INDIC_SCRIPTS_CHAR_CLASS = r'a-zA-Z\u0C00-\u0C7F\u0B80-\u0BFF\u0900-\u097F\u0C80-\u0CFF\u0D00-\u0D7F\u0600-\u06FF\u0A80-\u0AFF'

KNOWN_BUSINESS_KEYWORDS = {
    # English
    "traders", "enterprises", "stores", "kirana", "electricals", "hardware", "agency",
    "distributors", "mills", "wholesalers", "medicals", "cloths", "shop", "mart",
    "fertilizers", "automobiles", "services", "general", "supermarket", "jewellers",
    "textiles", "bakery", "hotel", "restaurant", "stationery", "trading", "industries",
    # Telugu
    "ట్రేడర్స్", "స్టోర్స్", "కిరాణా", "ఎంటర్‌ప్రైజెస్", "ఏజెన్సీ", "టెక్స్‌టైల్స్", "మెడికల్స్",
    # Tamil
    "டிரேடர்ஸ்", "ஸ்டோர்ஸ்", "மளிகை", "ஏஜென்சி", "டெக்ஸ்டைல்ஸ்", "மெடிக்கல்ஸ்", "ஹார்ட்வேர்",
    # Hindi
    "ट्रेडर्स", "स्टोर्स", "किराना", "एंटरप्राइजेज", "एजेंसी", "टेक्सटाइल्स", "मेडिकल्स", "हार्डवेयर",
    # Kannada
    "ಟ್ರೇಡರ್ಸ್", "ಸ್ಟೋರ್ಸ್", "ಕಿರಣ", "ಅಂಗಡಿ", "ಉದ್ಯಮ",
    # Malayalam
    "ട്രേഡേഴ്സ്", "സ്റ്റോർസ്", "സൂപ്പർമാർക്കറ്റ്", "കട",
    # Urdu
    "ٹریڈرز", "اسٹورز", "ایجنسی", "دکان", "کاروبار",
    # Gujarati
    "ટ્રેડર્સ", "સ્ટોર્સ", "દુકાન", "વેપાર", "પેઢી"
}

EXCLUDED_ACTOR_WORDS = {
    # Days of the week (All 8 Languages)
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "somavaram", "mangalavaram", "budhavaram", "guruvaram", "sukravaram", "sanivaram", "adivaram", "aadivaram",
    "thingal", "sevvaai", "budhan", "viyazhan", "velli", "sani", "njaayiru",
    "somwar", "mangalwar", "budhwar", "guruwar", "veervar", "shukrawar", "shaniwar", "raviwar", "itwar",
    "somavaara", "mangalavaara", "budhavaara", "guruvaara", "shukravaara", "shanivaara", "bhanuvaara",
    "thinkal", "chovva", "budhanaazhcha", "vyaazham", "velliaazhcha", "shaniaazhcha", "njaayaraazhcha",
    "peer", "jumerat", "jumma", "hafta",
    "somvar", "mangalvar", "budhvar", "guruvar", "shukravar", "shanivar", "ravivar",
    "సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం", "ఆదివారం",
    "திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு",
    "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "वीरवार", "शुक्रवार", "शनिवार", "रविवार", "इतवार",
    "ಸೋಮವಾರ", "ಮಂಗಳವಾರ", "ಬುಧವಾರ", "ಗುರುವಾರ", "ಶುಕ್ರವಾರ", "ಶನಿವಾರ", "ಭಾನುವಾರ",
    "തിങ്കൾ", "ചൊവ്വ", "ബുധൻ", "വ്യാഴം", "വെള്ളി", "ശനി", "ഞായർ",
    "پیر", "منگل", "بدھ", "جمعرات", "جمعہ", "اتوار",
    "સોમવાર", "મંગળવાર", "બુધવાર", "ગુરુવાર", "શુક્રવાર", "શનિવાર", "રવિવાર",
    
    # Temporal keywords across all 8 languages
    "yesterday", "today", "tomorrow", "ninna", "monna", "eroju", "ee roju", "nedu", "repu", "ellundi", "yelundi",
    "netru", "nethu", "mundhanal", "indru", "iniku", "innaiku", "naalai", "naalaikku", "marunaal",
    "kal", "aaj", "parson", "parso", "narson", "beeta kal", "aane wala kal",
    "ninne", "ivathu", "naale", "naadidhu", "innale", "innu", "mattedhu", "kale", "aaje", "paradive",
    "next", "last", "this", "vache", "vacche", "poyina", "kritham", "vaaram", "varam", "week", "nela", "month", "year",
    "adutha", "kadantha", "pona", "maadham", "masam", "agle", "pichle", "is", "hafte", "saptah", "mahine",
    "mundina", "hindina", "tingalu", "kazhinja", "aazhcha", "aavta", "pachhala", "gaya", "athwade", "mahine", "varsh",
    "morning", "evening", "night", "sayantram", "udayam", "madyanam", "afternoon", "daily",
    "காலை", "மாலை", "இரவு", "शाम", "दोपहर", "रात",
    "నిన్న", "మొన్న", "ఈరోజు", "రేపు", "ఎల్లుండి", "వచ్చే", "వారం", "నెల", "సంవత్సరం",
    "நேற்று", "இன்று", "நாளை", "அடுத்த", "கடந்த", "போன", "வாரம்", "மாதம்",
    "कल", "आज", "परसों", "अगले", "पिछले", "हफ्ते", "महीने", "साल",
    "ನೆನ್ನೆ", "ಇವತ್ತು", "ನಾಳೆ", "ನಾಡಿದ್ದು", "ಮುಂದಿನ", "ವಾರ", "ತಿಂಗಳು",
    "ഇന്നലെ", "ഇന്ന്", "നാളെ", "മറ്റന്നാൾ", "അടുത്ത", "ആഴ്ച", "മാസം",
    "کل", "آج", "پرسوں", "اگلے", "ہفتے", "مہینے", "سال",
    "કાલે", "આજે", "પરમ દિવસે", "આવતા", "અઠવાડિયે", "મહિને", "વર્ષ",
    
    # Financial terms
    "cash", "credit", "debit", "online", "gpay", "phonepe", "paytm", "upi", "cheque", "bank",
    "transfer", "account", "balance", "total", "amount", "money", "rupees", "rs", "inr",
    "dabbulu", "rupayalu", "chillara", "panam", "kaasu", "paise", "rupaye", "rokda", "rokkha", "rokad", "raqam",
    "remaining", "baki", "baaki", "pending", "advance", "udhari", "udhar", "discount", "bill", "invoice", "inv",
    "payment", "due", "refund", "interest", "saraku", "sarakku", "porul", "maal", "saman", "samaan", "goods", "stock", "khata", "hisaab",
    "already", "direct", "directly", "settled", "done", "complete", "completed", "full", "pura", "poora",
    "ఖాతా", "బాకీ", "రూపాయలు", "అడ్వాన్స్", "నగదు", "చెల్లింపు",
    "கணக்கு", "பாக்கி", "பணம்", "காசு", "அட்வான்ஸ்", "ரொக்கம்", "செலுத்துதல்",
    "खाता", "हिसाब", "बाकी", "रुपये", "पैसे", "एडवांस", "रोकड़ा", "उधार",
    "ಖಾತೆ", "ಬಾಕಿ", "ರೊಕ್ಕ", "പണം", "കണക്ക്", "ബാക്കി", "حساب", "رقم", "ખાતું", "બાકી", "રોકડ",
    
    # Verbs across 8 languages (Action, Modal, Communication & Auxiliary)
    "ivvali", "ravali", "ichadu", "ichindi", "icharu", "ichanu", "pampadu", "kattadu", "chellinchadu", "chesadu", "annadu", "istanu",
    "istha", "isthanu", "isthadu", "istadu", "isthaaru", "annaru", "cheppadu", "chepparu", "called", "phone", "chellincha", "chellinchanu", "chellincham",
    "kattesanu", "katta", "kattanu", "kattamu", "pampanu", "pampam", "ichesanu", "ichesha",
    "tharanum", "varanum", "koduthaar", "koduthen", "thandhaar", "thandhen", "kattinaar", "anuppinaar", "sonnaan", "tharen", "sonnaar", "pesinaan", "tharuven",
    "dena", "dena hai", "deni hai", "lena", "lena hai", "leni hai", "diya", "diye", "bheja", "chukaya", "bhara", "jama", "bola", "dega", "dunga", "kaha", "bataya",
    "kotte", "kottaru", "kodabeku", "barabeku", "kodtini", "kodtane", "thagondidini", "helida", "helidru",
    "koduthu", "thannu", "kodukkanam", "tharanund", "kittiyath", "tharaam", "paranju",
    "ada kiya", "wasool hua", "lena hai", "dena hai", "de dunga",
    "aapya", "chukavya", "malya", "levana che", "aapvana che", "aapshe", "aapish", "bolya",
    "give", "pay", "paid", "receive", "received", "sent", "send", "take", "need", "have", "owes", "owe",
    "ఇచ్చేశాను", "ఇచ్చేసాను", "ఇచ్చాను", "ఇచ్చాడు", "ఇచ్చింది", "ఇచ్చారు", "ఇవ్వాలి", "రావాలి", "చెల్లించా", "చెల్లించాను", "చెల్లించాం", "చెల్లించారు", "కట్టాడు", "కట్టాను", "పంపాడు", "పంపాను", "కొన్నాను", "కొన్నా", "అమ్మాను", "అమ్మా", "అన్నాడు", "అన్నారు", "ఇస్తాను", "ఇస్తా", "చెప్పాడు",
    "சொன்னார்", "சொன்னான்", "கொடுத்தேன்", "கொடுத்தார்", "தந்தார்", "தந்தேன்", "கட்டினார்", "வாங்கினேன்", "விற்றேன்", "தருகிறேன்",
    "दिया", "दिए", "दे दिया", "भेजा", "चुकाया", "भरा", "खरीदा", "बेचा", "बोला", "दूंगा", "देगा",
    "ಕೊಟ್ಟೆ", "ಕೊಟ್ಟರು", "ಕೊಡಬೇಕು", "ಬರಬೇಕು", "ತಗೊಂಡಿದ್ದೀನಿ", "ಹೇಳಿದ", "ಕೊಡ್ತೀನಿ",
    "വാങ്ങി", "വിറ്റു", "കൊടുത്തു", "തന്നു", "പറഞ്ഞു", "തരാം",
    "بولا", "کہا", "دیا", "ادا کیا", "وصول ہوا",
    "ખરીદ્યા", "વેચ્યા", "આપ્યા", "મળ્યા", "ચૂકવ્યા", "બોલ્યા", "આપીશ",

    # Prepositions, Postpositions & Case Markers
    "ki", "ku", "kku", "ukku", "ko", "se", "ne", "nundi", "nunchi", "irundhu", "kitta", "idam", "daggara", "vadda", "tho",
    "ige", "ge", "kke", "inda", "alli", "inu", "lekku", "ninnu", "thante", "mate", "pase", "pasethi", "thi", "keliye",
    "to", "from", "for", "in", "on", "at", "by", "with", "of", "into",
    "కి", "కు", "నుండి", "నుంచి", "తో", "లో", "దగ్గర", "వద్ద",
    "க்கு", "உக்கு", "இருந்து", "கிட்ட", "இடம்",
    "को", "से", "ने", "में", "पे", "पर", "के लिए", "के पास",
    "ಗೆ", "ಇಗೆ", "ಕ್ಕೆ", "ಇಂದ", "ಅಲ್ಲಿ",
    "ക്ക്", "ഇന്", "ലേക്ക്", "നിന്ന്",
    "کو", "سے", "نے", "کے لیے", "کے پاس",
    "ને", "થી", "પાસે", "માટે", "પાસેથી",
    
    # Pronouns across 8 languages (Native Scripts + Romanized)
    "nenu", "naaku", "naku", "memu", "maaku", "nuvvu", "meeru", "atanu", "aame", "vaaru", "vaallu", "ayana", "aayana", "vaadu", "vaadiki", "athanu", "athaniki",
    "నేను", "నాకు", "నాకి", "నాకొ", "నన్ను", "మేము", "మాకు", "నువ్వు", "మీరు", "అతను", "అతనికి", "ఆమె", "ఆమెకి", "వారు", "వారికి", "వాళ్ళు", "వాళ్లకి", "ఆయన", "ఆయనకి", "వాడు", "వాడికి",
    "naan", "enakku", "naanga", "engalukku", "neenga", "ungalukku", "avan", "avar", "avargal", "aval",
    "நான்", "எனக்கு", "நாங்கள்", "எங்களுக்கு", "நீ", "நீங்கள்", "உங்களுக்கு", "அவன்", "அவனுக்கு", "அவள்", "அவளுக்கு", "அவர்", "அவர்களுக்கு",
    "main", "mujhe", "mujhko", "hum", "humko", "humein", "aap", "tum", "usne", "unhone", "woh", "wo", "isse", "unse",
    "मैं", "मुझे", "मुझको", "हम", "हमको", "हमें", "तू", "तुम", "आप", "उसने", "उन्होंने", "वह", "वो",
    "naanu", "nanage", "naavu", "namage", "avaru", "avanu", "avalu", "avarige", "avanige", "avalige",
    "ನಾನು", "ನನಗೆ", "ನಾವು", "ನಮಗೆ", "ಅವನು", "ಅವನಿಗೆ", "ಅವಳು", "ಅವಳಿಗೆ", "ಅವರು", "ಅವರಿಗೆ",
    "njan", "enikku", "njangal", "njangalkku", "avan", "avalkku", "avar", "avarkku",
    "ഞാൻ", "എനിക്ക്", "ഞങ്ങൾ", "ഞങ്ങൾക്ക്", "അവൻ", "അവന്", "അവൾ", "അവൾക്ക്", "അവർ", "അവർക്ക്",
    "main", "mujhe", "mujhko", "hum", "humein", "aap", "tum", "usne", "unhone", "woh", "unhe",
    "میں", "مجھے", "مجھکو", "ہم", "ہمیں", "ہمکو", "تو", "تم", "آپ", "اس نے", "انہوں نے", "وہ",
    "hu", "mane", "ame", "amne", "tame", "temne", "tene",
    "હું", "મને", "અમે", "અમને", "તમે", "તેમણે", "તેણે", "તેઓ",
    "i", "me", "he", "she", "him", "her", "us", "they", "them", "my", "our", "his"
}

def _clean_actor_candidate(cand: str) -> str:
    tokens = [re.sub(rf'[^{INDIC_SCRIPTS_CHAR_CLASS}]', '', t) for t in cand.split()]
    tokens = [t for t in tokens if t]
    valid = []
    for t in tokens:
        tl = t.lower()
        if tl in EXCLUDED_ACTOR_WORDS or tl in ALL_INDIC_NUMERALS or len(tl) < 2:
            continue
            
        # Strip trailing postpositions across 8 languages
        for suffix in [
            "gariki", "annaki", "bhaiki", "sethki", "ki", "ku", "nundi", "nunchi",
            "kku", "ukku", "kitta", "idam", "irundhu", "avargalukku", "annavukku",
            "ko", "se", "ne", "bhaiya", "sethji",
            "ige", "ge", "kke", "inda", "alli", "avaru",
            "inu", "lekku", "ninnu", "thante",
            "keliye", "sahab", "janab",
            "mate", "pase", "pasethi", "bhai", "ben",
            "గారికి", "అన్నకి", "కి", "కు", "నుండి", "నుంచి",
            "க்கு", "உக்கு", "கிட்ட", "இடம்", "இருந்து",
            "को", "से", "ने", "जी", "भैया", "साहब",
            "ಗೆ", "ಇಗೆ", "ಕ್ಕೆ", "ಇಂದ",
            "ക്ക്", "ഇന്", "ലേക്ക്", "നിന്ന്",
            "کو", "سے", "صاحب",
            "ને", "થી", "પાસે", "ભાઈ", "બહેન"
        ]:
            if tl.endswith(suffix) and len(tl) > len(suffix) + 2:
                t = t[:-len(suffix)]
                tl = t.lower()
                break
                
        if (tl in KNOWN_BUSINESS_KEYWORDS or (tl not in EXCLUDED_ACTOR_WORDS and tl not in ALL_INDIC_NUMERALS)) \
           and len(tl) >= 2 \
           and not re.match(r'^\d+(\.\d+)?(k|thousand|thouzad|hazaar|aayiram|saavira|laksha|latcham|lakha|crore|kodi|koti)?$', tl):
            valid.append(t)
            
    if not valid:
        return ""
    name = " ".join(valid)
    return name.title() if not name.isupper() else name

class FinancialEntityExtractor:
    """
    Extracts structured financial slot entities across all 8 Indian languages and English.
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
            "invoices": [],
            "temporals": [],
            "status_flags": []
        }
        
        # 1. Date-First Extraction
        dates_extracted = TemporalExtractor.extract_dates(text)
        entities["temporals"] = dates_extracted
        
        # Mask date spans
        text_masked_for_amounts = text
        for d in dates_extracted:
            raw_span = d.get("raw_span", "")
            if raw_span and raw_span in text_masked_for_amounts:
                text_masked_for_amounts = text_masked_for_amounts.replace(raw_span, " " * len(raw_span))
                
        found_amounts = []
        
        # Check standard digits & currency symbols
        digit_patterns = [
            r'(?:rs\.?|inr|₹|రూ\.?|ரூ\.?|रु\.?|ರೂ\.?|രൂ\.?|روپے|રૂ\.?)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|thousand|thouzad|hazaar|hazar|aayiram|saavira|laksha|lakh|latcham|lac|crore|koti|kodi|karor)?\b',
            r'\b(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|thousand|thouzad|hazaar|hazar|aayiram|saavira|laksha|lakh|latcham|lac|crore|koti|kodi|karor|rupees|rupaye|rupayalu|panam|dabbulu|dharalu|rokkha|rokad|روپیہ)\b',
            r'\b(\d+(?:,\d+)*(?:\.\d+)?)\b'
        ]
        
        for pat in digit_patterns:
            for match in re.finditer(pat, text_masked_for_amounts, re.IGNORECASE):
                raw_num = match.group(1).replace(',', '')
                scale_word = match.group(2).lower() if len(match.groups()) >= 2 and match.group(2) else ""
                try:
                    val = float(raw_num)
                    if scale_word in ['k', 'thousand', 'thouzad', 'hazaar', 'hazar', 'aayiram', 'saavira']:
                        val *= 1000
                    elif scale_word in ['lakh', 'latcham', 'lac', 'laksha', 'laakh']:
                        val *= 100000
                    elif scale_word in ['crore', 'koti', 'kodi', 'karor']:
                        val *= 10000000
                    
                    if not any(a["value"] == val for a in found_amounts) and val > 0:
                        found_amounts.append({
                            "value": val,
                            "currency": "INR",
                            "raw_span": match.group(0).strip(),
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.98
                        })
                except ValueError:
                    continue
                    
        # Check spoken numbers across 8 languages
        _, spoken_amounts = IndicSpokenNumberParser.replace_spoken_numbers_in_text(text_masked_for_amounts)
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
            if clean and len(clean) >= 2 and clean.lower() not in EXCLUDED_ACTOR_WORDS and clean.lower() not in ALL_INDIC_NUMERALS:
                is_biz = any(k in clean.lower() for k in KNOWN_BUSINESS_KEYWORDS) or atype == "BUSINESS"
                if not any(a["name"].lower() == clean.lower() for a in entities["actors"]):
                    entities["actors"].append({
                        "name": clean,
                        "raw_span": raw_span,
                        "type": "BUSINESS" if is_biz else "PERSON",
                        "confidence": conf
                    })

        # Strategy 1: Ergative Subject markers (Hindi/Urdu/Gujarati/Kannada): "Amit ne kal 1500 diya", "राहुल ने 2000 जमा किया", "રમેશે 500 આપ્યા"
        ergative_pat = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+(?:\s+[{INDIC_SCRIPTS_CHAR_CLASS}]+)?)\s+(?:ne|నే|ने|ਨੇ|ને)(?:\s+|$|[.,!?])'
        for m in re.finditer(ergative_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.98)

        # Strategy 2: Multi-word Business Names across languages
        biz_pat = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+(?:\s+[{INDIC_SCRIPTS_CHAR_CLASS}]+){{0,2}}\s+(?:traders|enterprises|stores|kirana|electricals|hardware|agency|distributors|mills|wholesalers|medicals|shop|mart|jewellers|textiles|supermarket|automobiles|fertilizers|ట్రేడర్స్|స్టోర్స్|కిరాణా|டிரேடர்ஸ்|ஸ்டோர்ஸ்|ट्रेडर्स|स्टोर्स|किराना|ಟ್ರೇಡರ್ಸ್|സ്റ്റോർസ്|ટ્રેડર્સ))(?:\s+|$|[.,!?])'
        for m in re.finditer(biz_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), atype="BUSINESS", conf=0.97)

        # Strategy 3: Postpositional cues across 8 languages
        postpos_pat = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+(?:\s+[{INDIC_SCRIPTS_CHAR_CLASS}]+){{0,2}})\s+(?:gariki|annaki|bhaiki|sethki|ki|ku|nundi|nunchi|daggara|kku|ukku|kitta|idam|irundhu|ko|se|ke\s+paas|ige|ge|kke|inda|inu|lekku|thante|mate|pase|pasethi|గారికి|కి|కు|నుండి|க்கு|உக்கு|கிட்ட|இருந்து|को|से|के\s+पास|ಗೆ|ಇಗೆ|ಕ್ಕೆ|ಇಂದ|ക്ക്|ഇന്|ലേക്ക്|کو|سے|ને|થી|પાસે)(?:\s+|$|[.,!?])'
        for m in re.finditer(postpos_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.96)

        # Strategy 4: Direct Subject Inflow/Outflow across 8 languages
        subj_inflow_pat = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+(?:\s+[{INDIC_SCRIPTS_CHAR_CLASS}]+)?)\s+(?:naaku|naku|maaku|maku|enakku|mujhe|humko|nanage|enikku|mane|to me|to us|నాకు|எனக்கு|मुझे|ہمکو)?\s*(?:rs\.?|inr|₹)?\s*(?:\d+(?:,\d+)*(?:\.\d+)?)\s*(?:ichadu|ichindi|icharu|ichesadu|kattadu|pampadu|koduthaar|thandhaar|kattinaar|anuppinaar|diya|diye|bheja|jama kiya|kotte|kottaru|koduthu|thannu|wasool hua|aapya|malya|paid|transferred|sent|ఇచ్చాడు|కొடுத்தார்|தந்தார்|दिया|भेजा|ಕೊಟ್ಟರು|തന്നു|આપ્યા)(?:\s+|$|[.,!?])'
        for m in re.finditer(subj_inflow_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.98)

        # Strategy 5: Prepositional cues & Action commands
        prep_pat = rf'(?:^|\s+)(?:to|from|for|by|pay|give|paid to|transferred to|received from|due to|due from|payable to|receivable from|account of|record|add customer|add supplier)\s+([{INDIC_SCRIPTS_CHAR_CLASS}]+(?:\s+[{INDIC_SCRIPTS_CHAR_CLASS}]+){{0,2}})(?:\s+|$|[.,!?])'
        for m in re.finditer(prep_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.95)

        # Strategy 6: Honorifics across all 8 languages
        honorific_pat = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+(?:\s+[{INDIC_SCRIPTS_CHAR_CLASS}]+){{0,1}})\s+(?:garu|anna|gaaru|bhai|bhaiya|ji|seth|sethji|reddy|rao|saab|sir|avargal|aiyya|thambi|avaru|sahukara|sethru|chetan|chettan|ikka|sahib|janab|ben|kaka|గారు|அவர்கள்|ஐயா|जी|भैया|साहब|ಅವರು|ಅಣ್ಣ|ചേട്ടൻ|صاحب|ભાઈ|બહેન)(?:\s+|$|[.,!?])'
        for m in re.finditer(honorific_pat, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.95)

        # Strategy 7: Action Verbs following/preceding Name
        verb_pat_pre = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+)\s+(?:ichadu|ichindi|pampadu|kattadu|koduthaar|thandhaaru|kattinaar|diya|diye|bheja|kotte|kottaru|koduthu|thannu|aapya|malya|annadu|sonnaaru|bola|paranju|bolya|ఇచ్చాడు|కొடுத்தார்|தந்தார்|दिया|भेजा|ಕೊಟ್ಟರು|തന്നു|આપ્યા)(?:\s+|$|[.,!?])'
        for m in re.finditer(verb_pat_pre, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.94)

        verb_pat_post = rf'\b(?:transfer chesadu|ichesadu|ichadu|pampadu|ivvalasindi|ivvalsindi|ivvali|ravali|kattalsindi|kattadu|tharanum|varanum|dena|lena|bheja|kodabeku|barabeku|kodukkanam|tharanund|ada karna|aapvana|levana)\s+(?:to|for)?\s*([{INDIC_SCRIPTS_CHAR_CLASS}]+)\b'
        for m in re.finditer(verb_pat_post, text, re.IGNORECASE):
            add_actor(m.group(1), m.group(0), conf=0.93)

        # Strategy 8: Fallback Positional Subject / Object / Noun
        if not entities["actors"]:
            tokens = [re.sub(rf'[^{INDIC_SCRIPTS_CHAR_CLASS}]', '', t) for t in text.split()]
            tokens = [t for t in tokens if t]
            candidates = [t for t in tokens if t.lower() not in EXCLUDED_ACTOR_WORDS and t.lower() not in ALL_INDIC_NUMERALS and not re.match(r'^\d+(\.\d+)?(k|lakh)?$', t.lower())]
            if candidates:
                cand_name = candidates[0]
                add_actor(cand_name, cand_name, conf=0.90)

        # 3. Extract Payment Method
        for method_type, keywords in ALL_PAYMENT_METHODS.items():
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
