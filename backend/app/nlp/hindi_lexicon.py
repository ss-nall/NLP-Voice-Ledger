"""
Comprehensive Hindi Financial Lexicon, Grammar Markers, Spoken Numerals, and Vernacular Terms.
Supports Romanized Hindi (Hinglish), Devanagari Script (Unicode: 0x0900 - 0x097F), and Code-Mixed Transliterations.
"""

from typing import Dict, List, Set

# Hindi / Devanagari Unicode Range
HINDI_UNICODE_RANGE = (0x0900, 0x097F)

# Comprehensive Spoken Hindi Digits & Numbers to Integers
HINDI_NUMERALS: Dict[str, float] = {
    # 0
    "shunya": 0, "soonya": 0, "zero": 0, "zeero": 0, "sifar": 0, "शून्य": 0, "सिफर": 0, "ज़ीरो": 0,
    
    # 1 - 10
    "ek": 1, "aik": 1, "ik": 1, "one": 1, "एक": 1,
    "do": 2, "dho": 2, "two": 2, "दो": 2,
    "teen": 3, "tin": 3, "three": 3, "तीन": 3,
    "chaar": 4, "char": 4, "four": 4, "चार": 4,
    "paanch": 5, "panch": 5, "five": 5, "पांच": 5, "पाँच": 5,
    "chhe": 6, "chheh": 6, "six": 6, "छह": 6, "छः": 6, "छे": 6,
    "saat": 7, "sat": 7, "seven": 7, "सात": 7,
    "aath": 8, "ath": 8, "eight": 8, "आठ": 8,
    "nau": 9, "no": 9, "nine": 9, "नौ": 9,
    "das": 10, "dus": 10, "ten": 10, "दस": 10,
    
    # 11 - 19
    "gyarah": 11, "gyara": 11, "eleven": 11, "ग्यारह": 11,
    "barah": 12, "bara": 12, "twelve": 12, "बारह": 12,
    "terah": 13, "tera": 13, "thirteen": 13, "तेरह": 13,
    "chaudah": 14, "chauda": 14, "choudah": 14, "fourteen": 14, "चौदह": 14,
    "pandrah": 15, "pandra": 15, "fifteen": 15, "पंद्रह": 15,
    "solah": 16, "sola": 16, "sixteen": 16, "सोलह": 16,
    "satrah": 17, "satra": 17, "seventeen": 17, "सत्रह": 17,
    "atharah": 18, "athara": 18, "eighteen": 18, "अठारह": 18,
    "unnees": 19, "unnis": 19, "nineteen": 19, "उन्नीस": 19,
    
    # 20 - 90 (Tens)
    "bees": 20, "bis": 20, "twenty": 20, "बीस": 20,
    "tees": 30, "tis": 30, "thirty": 30, "तीस": 30,
    "chalis": 40, "chaalees": 40, "forty": 40, "चालीस": 40,
    "pachaas": 50, "pachas": 50, "fifty": 50, "पचास": 50,
    "saath": 60, "sath": 60, "sixty": 60, "साठ": 60,
    "sattar": 70, "seventy": 70, "सत्तर": 70,
    "assi": 80, "assee": 80, "eighty": 80, "अस्सी": 80,
    "nabbe": 90, "nabbey": 90, "navve": 90, "ninety": 90, "नब्बे": 90,
    
    # Fractions & Multipliers
    "dedh": 1.5, "dhai": 2.5, "डेढ़": 1.5, "ढाई": 2.5,
    "dedh hazaar": 1500, "डेढ़ हजार": 1500,
    "dhai hazaar": 2500, "ढाई हजार": 2500,
    "pachees": 25, "pachis": 25, "पच्चीस": 25, "paintees": 35, "पैंतीस": 35,
    "paentalis": 45, "पैंतालीस": 45, "pachpan": 55, "पचपन": 55,
    
    # Hundreds (100 - 900)
    "sau": 100, "so": 100, "ek sau": 100, "hundred": 100, "सौ": 100, "एक सौ": 100,
    "do sau": 200, "दो सौ": 200,
    "teen sau": 300, "तीन सौ": 300,
    "chaar sau": 400, "चार सौ": 400,
    "paanch sau": 500, "पांच सौ": 500, "पाँच सौ": 500,
    "chhe sau": 600, "छह सौ": 600,
    "saat sau": 700, "सात सौ": 700,
    "aath sau": 800, "आठ सौ": 800,
    "nau sau": 900, "नौ सौ": 900,
    
    # Thousands (1,000 - 90,000)
    "hazaar": 1000, "hazar": 1000, "ek hazaar": 1000, "thousand": 1000, "हजार": 1000, "एक हजार": 1000,
    "do hazaar": 2000, "dohazar": 2000, "दो हजार": 2000,
    "teen hazaar": 3000, "teenhazar": 3000, "तीन हजार": 3000,
    "chaar hazaar": 4000, "chaarhazar": 4000, "चार हजार": 4000,
    "paanch hazaar": 5000, "paanchhazar": 5000, "पांच हजार": 5000, "पाँच हजार": 5000,
    "chhe hazaar": 6000, "chhehazar": 6000, "छह हजार": 6000,
    "saat hazaar": 7000, "saathazar": 7000, "सात हजार": 7000,
    "aath hazaar": 8000, "aathhazar": 8000, "आठ हजार": 8000,
    "nau hazaar": 9000, "nauhazar": 9000, "नौ हजार": 9000,
    "das hazaar": 10000, "dashazar": 10000, "दस हजार": 10000,
    "pandrah hazaar": 15000, "pandrahhazar": 15000, "पंद्रह हजार": 15000,
    "bees hazaar": 20000, "beeshazar": 20000, "बीस हजार": 20000,
    "pachees hazaar": 25000, "pacheeshazar": 25000, "पच्चीस हजार": 25000,
    "tees hazaar": 30000, "teeshazar": 30000, "तीस हजार": 30000,
    "chalis hazaar": 40000, "chalishazar": 40000, "चालीस हजार": 40000,
    "pachaas hazaar": 50000, "pachashazar": 50000, "पचास हजार": 50000,
    "saath hazaar": 60000, "saathhazar": 60000, "साठ हजार": 60000,
    "sattar hazaar": 70000, "sattarhazar": 70000, "सत्तर हजार": 70000,
    "assi hazaar": 80000, "assihazar": 80000, "अस्सी हजार": 80000,
    "nabbe hazaar": 90000, "nabbehazar": 90000, "नब्बे हजार": 90000,
    
    # Lakhs & Crores
    "lakh": 100000, "laakh": 100000, "ek lakh": 100000, "lakhs": 100000, "लाख": 100000, "एक लाख": 100000,
    "do lakh": 200000, "दो लाख": 200000, "paanch lakh": 500000, "पांच लाख": 500000,
    "crore": 10000000, "kror": 10000000, "crores": 10000000, "ek crore": 10000000, "करोड़": 10000000, "एक करोड़": 10000000, "दो करोड़": 20000000
}

# Postpositions & Directional markers for Hindi
HINDI_DIRECTION_MARKERS = {
    # Postpositions attached to counterparties we are paying TO (Supplier / Outflow)
    "PAYABLE_POSTPOSITIONS": [
        "ko", "ke liye", "ke paas", "bhaiya ko", "sethji ko", "unko", "inko", "sir ko",
        "को", "के लिए", "के पास", "भैया को", "सेठजी को", "उनको", "इनको", "साहब को", "जी को"
    ],
    # Postpositions attached to counterparties we are receiving FROM (Customer / Inflow)
    "RECEIVABLE_POSTPOSITIONS": [
        "se", "ke paas se", "ki taraf se", "unse", "inse",
        "से", "के पास से", "की तरफ से", "उनसे", "इनसे"
    ],
    # Agent / Ergative postpositions attached to counterparty who performed action (Customer Giver)
    "AGENT_POSTPOSITIONS": [
        "ne", "usne", "unhone", "ने", "उसने", "उन्होंने"
    ],
    # Obligation / Future / Due Payable (Business has to pay supplier)
    "PAYABLE_VERBS": [
        "dena hai", "dena hoga", "chukana hai", "bharna hai", "pay karna hai", "deni hai",
        "dene hain", "bhejna hai", "dena banta hai", "transfer karna hai", "gpay karna hai", "dena",
        "देना है", "देना होगा", "चुकाना है", "भरना है", "पे करना है", "देनी है", "देने हैं",
        "भेजना है", "जमा करना है", "ट्रांसफर करना है"
    ],
    # Obligation / Due Receivable (Customer has to pay business / Asset)
    "RECEIVABLE_VERBS": [
        "lena hai", "aana hai", "milna hai", "baki hai", "pending hai", "vasool karna hai",
        "baaki hai", "udhar hai", "leni hai", "lene hain", "aane hain", "milne hain", "lena",
        "baaki banta hai", "baki bachta hai", "pending banta hai",
        "लेना है", "आना है", "मिलना है", "बाकी है", "पेन्डिंग है", "वसूल करना है",
        "उधार है", "लेनी है", "लेने हैं", "आने हैं", "बकाया है"
    ],
    # Customer paid business (reducing receivable balance)
    "PAID_BY_CUSTOMER_VERBS": [
        "diya", "diye", "de diya", "de diye", "chukaya", "bhara", "bheja", "bhej diya",
        "transfer kiya", "pay kiya", "gpay kiya", "phonepe kiya", "jama kiya", "aaya", "mil gaya",
        "de gaya", "jama karwaya", "settle kiya", "clear kiya",
        "दिया", "दिए", "दे दिया", "दे दिए", "चुकाया", "भरा", "भेजा", "भेज दिया",
        "ट्रांसफर किया", "पे किया", "जमा किया", "आया", "मिल गया", "दे गया", "सेटल किया", "क्लियर किया"
    ],
    # Business paid supplier (reducing payable balance)
    "PAID_BY_BUSINESS_VERBS": [
        "maine diya", "humne diya", "maine bhej diya", "humne bheja", "de chuka hoon",
        "pay kar diya", "transfer kar diya", "bhej diya", "jama kar diya", "chukta kiya",
        "मैंने दिया", "हमने दिया", "मैंने भेज दिया", "पे कर दिया", "ट्रांसफर कर दिया",
        "भेज दिया", "जमा कर दिया", "चुका दिया"
    ],
    # Promise verbs
    "PROMISE_VERBS": [
        "dene ko bola", "dega bola", "dunga bola", "bhejne ko bola", "kal dega bola",
        "dene ka wada kiya", "pay karunga bola", "transfer karunga bola", "de dunga bola",
        "देने को बोला", "दूंगा बोला", "देगा बोला", "भेजने को बोला", "पे करूंगा बोला", "दे दूंगा बोला"
    ],
    # Full settlement verbs
    "SETTLEMENT_VERBS": [
        "poora de diya", "pura payment kar diya", "sab clear kar diya", "hisaab clear ho gaya",
        "settle kar diya", "chutka kar diya", "pura hisaab barabar", "all clear",
        "पूरा दे दिया", "सब क्लियर कर दिया", "हिसाब चुकता कर दिया", "सेटल कर दिया",
        "पूरा पेमेंट कर दिया", "हिसाब बराबर"
    ],
    # Advance verbs
    "ADVANCE_VERBS": [
        "advance diya", "advance bheja", "advance jama kiya", "advance mila", "advance", "एडवांस"
    ],
    # Credit sale verbs
    "CREDIT_SALE_VERBS": [
        "maal diya", "samaan diya", "goods bheja", "udhar pe diya", "bill banaya", "becha",
        "माल दिया", "सामान दिया", "उधार पे दिया", "बिल बनाया", "बेचा"
    ],
    # Purchase verbs
    "PURCHASE_VERBS": [
        "maal kharida", "samaan mangwaya", "stock mangwaya", "purchase kiya", "kharida",
        "माल खरीदा", "सामान मंगवाया", "स्टॉक मंगवाया", "खरीदा"
    ]
}

# Temporal dictionary for Hindi
HINDI_TEMPORAL_LEXICON = {
    "kal": 1,
    "beeta kal": -1, "pichla kal": -1, "yesterday": -1, "बीता कल": -1,
    "parson": 2, "parso": 2, "narson": 3, "परसों": 2, "नरसों": 3,
    "aaj": 0, "today": 0, "आज": 0,
    "aane wala kal": 1, "tomorrow": 1, "कल": 1,
    "agle hafte": 7, "agle saptah": 7, "next week": 7, "अगले हफ्ते": 7, "अगले सप्ताह": 7,
    "pichle hafte": -7, "pichla saptah": -7, "last week": -7, "पिछले हफ्ते": -7, "पिछले सप्ताह": -7,
    "is hafte": 0, "is saptah": 0, "this week": 0, "इस हफ्ते": 0, "इस सप्ताह": 0,
    "agle mahine": 30, "next month": 30, "अगले महीने": 30,
    "pichle mahine": -30, "last month": -30, "पिछले महीने": -30
}

HINDI_DAYS_OF_WEEK = {
    "somwar": 0, "somvaar": 0, "monday": 0, "सोमवार": 0,
    "mangalwar": 1, "mangalvaar": 1, "tuesday": 1, "मंगलवार": 1,
    "budhwar": 2, "budhvaar": 2, "wednesday": 2, "बुधवार": 2,
    "guruwar": 3, "veervar": 3, "guruvaar": 3, "thursday": 3, "गुरुवार": 3, "वीरवार": 3, "बृहस्पतिवार": 3,
    "shukrawar": 4, "shukravaar": 4, "friday": 4, "शुक्रवार": 4, "जुमे": 4,
    "shaniwar": 5, "shanivaar": 5, "saturday": 5, "शनिवार": 5, "सनीचर": 5,
    "raviwar": 6, "ravivaar": 6, "itwar": 6, "sunday": 6, "रविवार": 6, "इतवार": 6
}

HINDI_MONTHS = {
    "जनवरी": 1, "फ़रवरी": 2, "फरवरी": 2, "मार्च": 3, "अप्रैल": 4, "मई": 5, "जून": 6,
    "जुलाई": 7, "अगस्त": 8, "सितंबर": 9, "सितम्बर": 9, "अक्टूबर": 10, "नवंबर": 11, "नवम्बर": 11, "दिसंबर": 12, "दिसम्बर": 12
}

HINDI_HONORIFICS = ["ji", "bhaiya", "bhai", "sethji", "saab", "sir", "babuji", "shree", "जी", "भैया", "सेठजी", "साहब", "श्री", "बाबूजी"]

HINDI_BUSINESS_TERMS = {
    "maal": "goods", "samaan": "items/goods", "kirana": "groceries",
    "baaki": "outstanding_balance", "baki": "outstanding_balance", "udhar": "credit",
    "jama": "credit_entry", "kharcha": "debit_expense", "paise": "money", "rupaye": "money",
    "chillara": "small_cash", "khata": "account_ledger", "hisaab": "account/settlement", "rokda": "cash"
}
