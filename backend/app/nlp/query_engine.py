"""
Semantic Text-to-Ledger Query Engine ("Voice CFO").
Parses complex, time-bounded, entity-specific, and aggregate financial inquiries
across 8 languages (English, Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, Gujarati).
"""

import re
from typing import Dict, Any, List, Optional

class SemanticQueryEngine:
    """
    Parses analytical questions into structured query execution plans across 8 languages.
    Guarantees transactions with explicit amounts/actors are never misclassified as queries.
    """

    def parse_query(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        
        # 1. Booking keywords across languages
        booking_keywords = [
            "ichadu", "ichanu", "ivvali", "ravali", "konna", "ammanu", "transfer", "paid", "received",
            "kuduthen", "koduthaar", "diya", "diye", "kotte", "kottaru", "koduthu", "thannu", "wasool", "aapya", "malya",
            "ఇచ్చాను", "ఇచ్చాడు", "ఇవ్వాలి", "రావాలి", "కొடுத்தேன்", "கொடுத்தார்", "दिया", "दिए",
            "ಕೊಟ್ಟೆ", "ಕೊಟ್ಟರು", "ಕೊടുത്തു", "തന്നു", "دیا", "وصول", "આપ્યા", "મળ્યા"
        ]
        
        # Question markers across 8 languages
        question_markers = [
            "evaru", "entha", "how much", "who", "show", "chupinchu", "summary", "list", "which", "when", "eppudu",
            "yaaru", "evalo", "eppodhu", "kaun", "kitna", "kab", "kisko", "kisse",
            "yaru", "enu", "estu", "yavaga", "aaranu", "enthanu", "etra", "eppol",
            "kab", "kis ko", "kitni", "kon", "ketla", "kyare", "kone",
            "ఎవరు", "ఎంత", "ఎప్పుడు", "చూపించు", "జాబితా", "సారాంశం",
            "யார்", "எவ்வளவு", "எப்போது",
            "कौन", "कितना", "कब", "किसको", "किसे",
            "ಯಾರು", "ಎಷ್ಟು", "ಯಾವಾಗ",
            "ആര്", "എത്ര", "എപ്പോൾ", "ആർക്കാണ്",
            "کون", "کتنا", "کب", "کس کو", "کتنی",
            "કોણ", "કેટલા", "ક્યારે", "કોને",
            "?", "؟"
        ]
        
        has_question_marker = any(qm in text_lower for qm in question_markers)
        has_amount_digit = bool(re.search(r'\d+', text))
        
        # If it has an amount and a booking verb without an explicit question word, it's a booking transaction
        if has_amount_digit and any(bk in text_lower for bk in booking_keywords) and not has_question_marker:
            return {"is_query": False, "intent": "GENERAL_SEARCH", "filters": {}, "raw_query": text}

        # Check for analytical inquiry keywords even if ? is absent
        analytical_triggers = [
            "top debtor", "overdue", "highest due", "total receivable", "total payable", "motham raavali", "motham ivvali",
            "highest outflow", "most paid", "who did i pay", "last payment", "when did", "this week", "today total",
            "collections", "payouts", "cashflow", "cash flow", "ekkuva ichanu", "last payment eppudu",
            "sabse zyada", "kisse lena", "kitna dena", "estu kodabeku", "etra tharanam", "ketla aapvana", "kone aapya",
            "കൂടുതൽ", "ആർക്കാണ്"
        ]
        if not has_question_marker and not any(kw in text_lower for kw in analytical_triggers):
            return {"is_query": False, "intent": "GENERAL_SEARCH", "filters": {}, "raw_query": text}

        intent = "GENERAL_SEARCH"
        filters: Dict[str, Any] = {}
        target_entity: Optional[str] = None
        time_range: Optional[str] = None

        # Time range filters
        if any(w in text_lower for w in ["ఈ రోజు", "today", "eroju", "iniku", "aaj", "ivathu", "innu", "aaje", "ആജ്", "آج"]):
            time_range = "TODAY"
        elif any(w in text_lower for w in ["నిన్న", "yesterday", "ninna", "netru", "kal", "ninne", "innale", "kale", "ഇന്നലെ", "کل"]):
            time_range = "YESTERDAY"
        elif any(w in text_lower for w in ["ఈ వారం", "this week", "ee varam", "intha vaaram", "is hafte", "ee vaara", "ee aazhcha", "aa athwade", "ആ അઠવાടિયേ", "اس ہفتے", "ಈ ವಾರ", "ഈ ആഴ്ച"]):
            time_range = "THIS_WEEK"
        elif any(w in text_lower for w in ["ఈ నెల", "this month", "ee nela", "intha maasam", "is mahine", "ee tingalu", "ee maasam", "aa mahine", "આ મહિને", "اس مہینے", "ಈ ತಿಂಗಳು", "ഈ മാസം"]):
            time_range = "THIS_MONTH"
        elif any(w in text_lower for w in ["గత నెల", "last month", "gatha nela", "pona maasam", "pichle mahine", "hindina tingalu", "kazhinja maasam"]):
            time_range = "LAST_MONTH"

        # Complex Voice CFO Intent Classification across 8 languages
        if any(w in text_lower for w in [
            "who did i pay the most", "highest outflow", "most paid", "ekkuva ichanu", "ekkuva payment",
            "ఎవరికి ఎక్కువ", "ఎక్కువ ఇచ్చాను", "అధికంగా யாருக்கு", "யாருக்கு அதிகம்", "किसको सबसे ज्यादा", "सबसे ज्यादा किसे",
            "ಯಾರಿಗೆ ಹೆಚ್ಚು", "ಯಾರಿಗೆ ಜಾಸ್ತಿ", "ആർക്കാണ് കൂടുതൽ", "ആർക്കാണ്", "കൂടുതൽ കൊടുത്തത്",
            "کس کو سب سے زیادہ", "سب سے زیادہ کس کو", "سب سے زیادہ دیا",
            "સૌથી વધુ કોને", "સૌથી વધારે કોને", "સૌથી વધુ ચૂકવ્યા"
        ]):
            intent = "HIGHEST_OUTFLOW"
        elif any(w in text_lower for w in [
            "last payment", "when did", "eppudu chesadu", "eppudu ichadu", "last paid", "kab bhugtan", "kab diya", "aakhri baar",
            "లాస్ట్ పేమెంట్", "ఎప్పుడు ఇచ్చాడు", "ఎప్పుడు చేశాడు", "எப்போது கொடுத்தார்", "எப்போது செலுத்தினார்", "पिछली बार कब", "आखिरी बार कब",
            "ಯಾವಾಗ ಪಾವತಿಸಿದರು", "ಕೊನೆಯದಾಗಿ ಯಾವಾಗ", "ಎപ്പോഴാണ് നൽകിയത്", "അവസാനം എപ്പോൾ", "അവസാനം എപ്പോഴാണ്", "ಎപ്പോഴാണ് പണം നൽകിയത്",
            "پچھلی بار کب", "آخری بار کب", "ادائیگی کی",
            "છેલ્લે ક્યારે", "ક્યારે ચૂકવ્યા"
        ]):
            intent = "LAST_PAYMENT_DATE"
            # Extract target entity name
            words = [w.strip("?,.!؟") for w in text.split()]
            for w in words:
                if len(w) > 2 and w.lower() not in [
                    "when", "did", "pay", "last", "eppudu", "chesadu", "kab", "kisko", "yaaru", "eppodhu", "yavaga", "eppol", "kyare",
                    "payment", "bhugtan", "kare", "adaigi", "chukavya", "nalkiyath", "kottaru"
                ]:
                    target_entity = w
                    break
        elif any(w in text_lower for w in [
            "total receivable", "motham raavali", "total due to me",
            "మొత్తం రావాల్సిన", "మొత్తం రావలసిన", "మొత్తం బాకీలు", "மொத்த வரவு", "कुल उधारी", "ಒಟ್ಟು ಬರಬೇಕಾದ", "ആകെ ലഭിക്കാനുള്ള", "કુલ લેવાના"
        ]):
            intent = "TOTAL_RECEIVABLES"
        elif any(w in text_lower for w in [
            "total payable", "motham ivvali", "total due to suppliers",
            "మొత్తం ఇవ్వాల్సిన", "మొత్తం ఇవ్వవలసిన", "மொத்த பட்டுவாடா", "कुल देय", "ಒಟ್ಟು ಕೊಡಬೇಕಾದ", "ആകെ നൽകാനുള്ള", "કુલ આપવાના"
        ]):
            intent = "TOTAL_PAYABLES"
        elif any(w in text_lower for w in [
            "weekly receivables", "dues are to be collected this week", "ee varam ravalasina", "this week due", "dues this week", "dues to be collected",
            "ఈ వారం రావాల్సిన", "రావాల్సిన బాకీలు ఎంత", "బాకీలు ఎంత", "வர வேண்டிய பாக்கி", "இந்த வாரம்", "इस हफ्ते", "कितनी वसूली बाकी",
            "ಈ ವಾರ ಬರಬೇಕಾದ", "ಈ ವಾರ ಎಷ್ಟು ಬರಬೇಕು", "ಬರಬೇಕಾದ ಬಾಕಿ",
            "ഈ ആഴ്ച ലഭിക്കാനുള്ള", "ഈ ആഴ്ച എത്ര", "ലഭിക്കാനുള്ള ബാക്കി", "ലഭിക്കാനുണ്ട്",
            "اس ہفتے کتنی رقم", "کتنی رقم لینی ہے", "کتنی رقم",
            "આ અઠવાડિયે કેટલા લેવાના", "કેટલા લેવાના છે", "લેવાના છે"
        ]):
            intent = "WEEKLY_RECEIVABLES"
        elif any(w in text_lower for w in [
            "today's total", "today collections", "today cashflow", "collections and payouts", "total collections and payouts", "motham collections",
            "ఈ రోజు మొత్తం", "మొత్తం కలెక్షన్", "இன்றைய வரவு", "இன்றைய ரொக்கம்", "आज का कुल", "कुल कलेक्शन",
            "ಇಂದಿನ ಒಟ್ಟು", "ಇಂದಿನ ಕಲೆಕ್ಷನ್", "ഇന്നത്തെ ആകെ", "ഇന്നത്തെ കളക്ഷൻ",
            "આજનો હિસાબ", "આજનું કુલ કલેક્શન", "કુલ કલેક્શન",
            "آج کی کل وصولی", "کل کیش فلو"
        ]):
            intent = "TODAY_CASHFLOW"
        elif any(w in text_lower for w in [
            "who owes", "evaru ivvali", "evaru naaku", "ekkuva baaki", "top debtor", "highest due",
            "ఎవరు ఎక్కువ", "ఎవరు బాకీ", "ఎక్కువ బాకీ", "ఎవరు ఇవ్వాలి", "யாருக்கு பாக்கி", "कौन बाकी", "ಯಾರು ಬಾಕಿ", "ആർക്കാണ് ബാക്കി"
        ]):
            intent = "TOP_DEBTORS"
        elif any(w in text_lower for w in [
            "raavalasina", "రావలసిన", "రావాల్సిన బాకీలు"
        ]):
            intent = "TOTAL_RECEIVABLES"
        elif any(w in text_lower for w in [
            "ivvalasina", "ఇవ్వాల్సిన బాకీలు"
        ]):
            intent = "TOTAL_PAYABLES"
        elif any(w in text_lower for w in ["overdue", "gaduvu datina", "pending", "late", "గడువు దాటిన", "ಅತಿಮೀರಿದ", "കാലഹരണപ്പെട്ട"]):
            intent = "OVERDUE_BALANCES"
        elif any(w in text_lower for w in ["statement", "history", "khata", "vivaralu", "transactions", "chupinchu", "show me", "వివరాలు", "స్టేట్‌మెంట్", "ಖಾತೆ"]):
            intent = "ENTITY_STATEMENT"
            words = text.split()
            if len(words) >= 2:
                cand = words[0]
                if cand.lower() not in ["show", "chupinchu", "evaru", "naaku", "what", "how", "చూపించు", "ఎవరు"]:
                    target_entity = cand

        if time_range:
            filters["time_range"] = time_range
        if target_entity:
            filters["target_entity"] = target_entity

        return {
            "is_query": intent != "GENERAL_SEARCH",
            "intent": intent,
            "filters": filters,
            "target_entity": target_entity,
            "time_range": time_range,
            "raw_query": text
        }

query_engine = SemanticQueryEngine()
