"""
Comprehensive Tamil Financial Lexicon, Grammar Markers, Spoken Numerals, and Vernacular Terms.
Supports Romanized Tamil (Tanglish), Tamil Script (Unicode: 0x0B80 - 0x0BFF), and Code-Mixed Transliterations.
"""

from typing import Dict, List, Set

# Tamil Unicode Range
TAMIL_UNICODE_RANGE = (0x0B80, 0x0BFF)

# Comprehensive Spoken Tamil Digits & Numbers to Integers
TAMIL_NUMERALS: Dict[str, int] = {
    # 0
    "poojyam": 0, "poojiyam": 0, "sulliyam": 0, "zero": 0, "zeero": 0, "பூஜ்ஜியம்": 0, "சுழியம்": 0,
    
    # 1 - 10
    "ondru": 1, "onnu": 1, "oru": 1, "ore": 1, "onru": 1, "one": 1, "ஒன்று": 1, "ஒன்னு": 1, "ஒரு": 1,
    "irandu": 2, "rendu": 2, "erandu": 2, "two": 2, "இரண்டு": 2, "ரெண்டு": 2,
    "moondru": 3, "moonu": 3, "mundru": 3, "three": 3, "மூன்று": 3, "மூணு": 3,
    "naangu": 4, "naalu": 4, "nalu": 4, "four": 4, "நான்கு": 4, "நாலு": 4,
    "aindhu": 5, "anju": 5, "ainthu": 5, "ayindhu": 5, "five": 5, "ஐந்து": 5, "அஞ்சு": 5,
    "aaru": 6, "six": 6, "ஆறு": 6,
    "yezhu": 7, "ezhu": 7, "yelu": 7, "elu": 7, "seven": 7, "ஏழு": 7,
    "ettu": 8, "eight": 8, "எட்டு": 8,
    "onbadhu": 9, "ombodhu": 9, "onpathu": 9, "ombadhu": 9, "nine": 9, "ஒன்பது": 9, "ஒம்போது": 9,
    "pathu": 10, "patthu": 10, "ten": 10, "பத்து": 10,
    
    # 11 - 19
    "pathinondru": 11, "pathinonnu": 11, "patthinonnu": 11, "eleven": 11, "பதினொன்று": 11, "பதினொன்னு": 11,
    "pannirandu": 12, "panrendu": 12, "panirendu": 12, "twelve": 12, "பன்னிரண்டு": 12, "பன்னிரெண்டு": 12,
    "pathinmoondru": 13, "pathimoonu": 13, "patthimoonu": 13, "thirteen": 13, "பதின்மூன்று": 13, "பindustryமூணு": 13, "பத்துமூணு": 13, "பதcoreமூன்று": 13, "பதின்மூணு": 13,
    "pathinaangu": 14, "pathinaalu": 14, "patthinaalu": 14, "fourteen": 14, "பதினான்கு": 14, "பதினாலு": 14,
    "pathinaindhu": 15, "pathinanju": 15, "patthinanju": 15, "fifteen": 15, "பதினைந்து": 15, "பதினஞ்சு": 15,
    "pathinaaru": 16, "patthinaaru": 16, "sixteen": 16, "பதினாறு": 16,
    "pathinezhu": 17, "patthinezhu": 17, "seventeen": 17, "பதினேழு": 17,
    "padhinettu": 18, "pathinettu": 18, "eighteen": 18, "பதினெட்டு": 18,
    "patthonbadhu": 19, "patthombadhu": 19, "pathombadhu": 19, "nineteen": 19, "பத்தொன்பது": 19,
    
    # 20 - 90 (Tens)
    "irubadhu": 20, "iruvadhu": 20, "iravathu": 20, "irubathu": 20, "twenty": 20, "இருபது": 20,
    "muppadhu": 30, "muppathu": 30, "muppawthu": 30, "thirty": 30, "முப்பது": 30,
    "naarpathu": 40, "naarpadhu": 40, "nalpathu": 40, "nalpadhu": 40, "forty": 40, "நாற்பது": 40,
    "aimbadhu": 50, "aimbathu": 50, "ambadhu": 50, "ambathu": 50, "fifty": 50, "ஐம்பது": 50, "அம்பது": 50,
    "arubadhu": 60, "arubathu": 60, "aruvadhu": 60, "sixty": 60, "அறுபது": 60,
    "ezhubadhu": 70, "ezhubathu": 70, "eluvadhu": 70, "seventy": 70, "எழுபது": 70,
    "enbhadhu": 80, "enbadhu": 80, "enbathu": 80, "eighty": 80, "எண்பது": 80,
    "thonnooru": 90, "thonooru": 90, "thonnuru": 90, "ninety": 90, "தொண்ணூறு": 90,
    
    # Hundreds (100 - 900)
    "nooru": 100, "nuru": 100, "oru nooru": 100, "hundred": 100, "நூறு": 100, "ஒரு நூறு": 100,
    "irunooru": 200, "rendu nooru": 200, "இருநூறு": 200, "ரெண்டு நூறு": 200,
    "munnooru": 300, "moonu nooru": 300, "முந்நூறு": 300, "மூணு நூறு": 300,
    "naanooru": 400, "naalu nooru": 400, "நானூறு": 400, "நாலு நூறு": 400,
    "ainooru": 500, "anju nooru": 500, "ayinooru": 500, "ஐந்நூறு": 500, "அஞ்சு நூறு": 500,
    "aranooru": 600, "aaru nooru": 600, "அறுநூறு": 600, "ஆறு நூறு": 600,
    "ezhunooru": 700, "ezhu nooru": 700, "எழுநூறு": 700, "ஏழு நூறு": 700,
    "ennooru": 800, "ettu nooru": 800, "எண்ணூறு": 800, "எட்டு நூறு": 800,
    "thollayiram": 900, "tholaayiram": 900, "ombadhu nooru": 900, "தொள்ளாயிரம்": 900,
    
    # Thousands (1,000 - 90,000)
    "aayiram": 1000, "ayiram": 1000, "oru aayiram": 1000, "thousand": 1000, "ஆயிரம்": 1000, "ஒரு ஆயிரம்": 1000,
    "irandaayiram": 2000, "rendaayiram": 2000, "rendu aayiram": 2000, "இரண்டாயிரம்": 2000, "ரெண்டாயிரம்": 2000, "ரெண்டு ஆயிரம்": 2000,
    "moovaayiram": 3000, "moonaayiram": 3000, "moonu aayiram": 3000, "மூவாயிரம்": 3000, "மூணு ஆயிரம்": 3000,
    "naalaayiram": 4000, "naalu aayiram": 4000, "நாலாயிரம்": 4000, "நாலு ஆயிரம்": 4000,
    "aiyyaayiram": 5000, "anjaayiram": 5000, "anju aayiram": 5000, "aindhaayiram": 5000, "ஐந்தாயிரம்": 5000, "அஞ்சாயிரம்": 5000, "ஐந்து ஆயிரம்": 5000,
    "aaraayiram": 6000, "aaru aayiram": 6000, "ஆறாயிரம்": 6000, "ஆறு ஆயிரம்": 6000,
    "ezhaayiram": 7000, "ezhu aayiram": 7000, "ஏழாயிரம்": 7000, "ஏழு ஆயிரம்": 7000,
    "ettaayiram": 8000, "ettu aayiram": 8000, "எட்டாயிரம்": 8000, "எட்டு ஆயிரம்": 8000,
    "onbadhaayiram": 9000, "onbadhu aayiram": 9000, "ஒன்பதாயிரம்": 9000, "ஒன்பது ஆயிரம்": 9000,
    "patthaayiram": 10000, "pathu aayiram": 10000, "பத்தாயிரம்": 10000, "பத்து ஆயிரம்": 10000,
    "pathinanjaayiram": 15000, "pathinaindhaayiram": 15000, "பதினைந்தாயிரம்": 15000, "பதினஞ்சாயிரம்": 15000,
    "irubadhaayiram": 20000, "iruvadhadhaayiram": 20000, "irubadhu aayiram": 20000, "இருபதாயிரம்": 20000, "இருபது ஆயிரம்": 20000,
    "irubathaindhaayiram": 25000, "irubathanjaayiram": 25000, "இருபத்தைந்தாயிரம்": 25000, "இருபத்தஞ்சாயிரம்": 25000,
    "muppadhaayiram": 30000, "muppadhu aayiram": 30000, "முப்பதாயிரம்": 30000, "முப்பது ஆயிரம்": 30000,
    "naarpathaayiram": 40000, "naarpathu aayiram": 40000, "நாற்பதாயிரம்": 40000, "நாற்பது ஆயிரம்": 40000,
    "aimbadhaayiram": 50000, "ambadhaayiram": 50000, "aimbadhu aayiram": 50000, "ஐம்பதாயிரம்": 50000, "அம்பதாயிரம்": 50000, "ஐம்பது ஆயிரம்": 50000,
    "arubadhaayiram": 60000, "arubadhu aayiram": 60000, "அறுபதாயிரம்": 60000, "அறுபது ஆயிரம்": 60000,
    "ezhubadhaayiram": 70000, "ezhubadhu aayiram": 70000, "எழுபதாயிரம்": 70000, "எழுபது ஆயிரம்": 70000,
    "enbadhaayiram": 80000, "enbadhu aayiram": 80000, "எண்பதாயிரம்": 80000, "எண்பது ஆயிரம்": 80000,
    "thonnooraayiram": 90000, "thonnooru aayiram": 90000, "தொண்ணூறாயிரம்": 90000,
    
    # Lakhs & Crores
    "latcham": 100000, "patcham": 100000, "lakh": 100000, "lakhs": 100000, "oru latcham": 100000, "patcham": 100000,
    "இலட்சம்": 100000, "லட்சம்": 100000, "ஒரு லட்சம்": 100000, "ரெண்டு லட்சம்": 200000, "ஐந்து லட்சம்": 500000,
    "kodi": 10000000, "koti": 10000000, "crore": 10000000, "crores": 10000000, "oru kodi": 10000000,
    "கோடி": 10000000, "ஒரு கோடி": 10000000, "ரெண்டு கோடி": 20000000
}

# Postpositions & Directional markers for Tamil
TAMIL_DIRECTION_MARKERS = {
    # Postpositions attached to counterparties we are paying TO (Supplier / Outflow)
    "PAYABLE_POSTPOSITIONS": [
        "ukku", "kku", "idam", "kitta", "avargalukku", "annavukku", "bhaikku", "sethkku",
        "க்கு", "உக்கு", "அவர்களுக்கு", "அண்ணாவுக்கு", "கிட்ட", "இடம்", "சேத்துக்கு", "பாய்க்கு"
    ],
    # Postpositions attached to counterparties we are receiving FROM (Customer / Inflow)
    "RECEIVABLE_POSTPOSITIONS": [
        "irundhu", "idamirundhu", "kitterundhu", "kitta irundhu", "idam irundhu",
        "இருந்து", "இடமிருந்து", "கிட்ட இருந்து", "கிட்டயிருந்து"
    ],
    # Obligation / Future / Due Payable (Business has to pay supplier)
    "PAYABLE_VERBS": [
        "thara vendum", "tharanum", "kodukka vendum", "kodukkanum", "kattanam", "kattanum",
        "pay pannanum", "kodukanum", "thara vendiyadhu", "kattavendum", "kattavendiyadhu",
        "thara vendi irukku", "kodukka vendi irukku", "anuppa vendum", "anuppanum",
        "தர வேண்டும்", "தரனும்", "கொடுக்க வேண்டும்", "கொடுக்கனும்", "கட்ட வேண்டும்", "கட்டனும்",
        "செலுத்த வேண்டும்", "செலுத்தனும்", "பே பண்ணனும்", "அனுப்ப வேண்டும்", "அனுப்பனும்"
    ],
    # Obligation / Due Receivable (Customer has to pay business / Asset)
    "RECEIVABLE_VERBS": [
        "vara vendum", "varanum", "vaanga vendum", "vaanganum", "baki irukku", "pending irukku",
        "vara vendiyadhu", "vara vendi irukku", "vasool pannanum", "collect pannanum",
        "thara vendum", "baaki irukku", "kadhan irukku", "baki", "baaki", "pending",
        "வர வேண்டும்", "வரனும்", "வாங்க வேண்டும்", "வாங்கனும்", "பாக்கி இருக்கு", "பாக்கி",
        "பெண்டிங் இருக்கு", "பெண்டிங்", "வசூல் செய்ய வேண்டும்", "வசூல் பண்ணனும்"
    ],
    # Customer paid business (reducing receivable balance)
    "PAID_BY_CUSTOMER_VERBS": [
        "koduthaar", "koduthaan", "koduthu vittar", "koduthutaar", "koduthutaaru", "koduthaaru",
        "thandhaar", "thandhaaru", "thandhaan", "kattinaar", "kattitaar", "kattitaaru",
        "anuppinaar", "anupinaar", "anuppitaaru", "vanthathu", "vanthuruchu", "vanthuduchu",
        "pay pannitaaru", "pay pannaar", "gpay pannaar", "phonepe pannaar", "transfer pannaar", "settle pannaar",
        "கொடுத்தார்", "கொடுத்தான்", "கொடுத்துட்டார்", "கொடுத்துட்டாரு", "தந்தார்", "தந்தாரு",
        "கட்டினார்", "கட்டிட்டார்", "கட்டிட்டாரு", "அனுப்பினார்", "அனுப்பிட்டார்",
        "வந்தது", "வந்துருச்சு", "வந்துடுச்சு", "செட்டில் பண்ணிட்டார்", "பே பண்ணிட்டார்"
    ],
    # Business paid supplier (reducing payable balance)
    "PAID_BY_BUSINESS_VERBS": [
        "koduthen", "koduthom", "koduthuten", "koduthuttom", "thandhen", "thandhom",
        "kattinen", "kattinom", "kattiten", "kattittom", "anuppinen", "anuppinom",
        "pay pannen", "pay pannom", "transfer pannen", "transfer pannom", "gpay pannen", "settle pannen",
        "கொடுத்தேன்", "கொடுத்தோம்", "கொடுத்துட்டேன்", "கொடுத்துட்டோம்", "தந்தேன்", "தந்தோம",
        "கட்டினேன்", "கட்டினோம்", "கட்டிட்டேன்", "கட்டிட்டோம்", "அனுப்பினேன்", "அனுப்பினோம்",
        "பே பண்ணேன்", "பே பண்ணோம்", "டிரான்ஸ்பர் பண்ணேன்", "செட்டில் பண்ணேன்"
    ],
    # Promise verbs
    "PROMISE_VERBS": [
        "tharen nu sonnaan", "tharen nu sonnaaru", "tharuven nu sonnaaru", "tharaen nu sonnaaru",
        "kattren nu sonnaan", "kattren nu sonnaaru", "kodukren nu sonnaan", "kodukren nu sonnaaru",
        "pay panren nu sonnaar", "transfer panren nu sonnaar",
        "தரேன்னு சொன்னார்", "தரேன்னு சொன்னான்", "தருவேன்னு சொன்னார்", "கொடுக்கிறேன்னு சொன்னார்",
        "கட்டறேன்னு சொன்னார்", "செலுத்துறேன்னு சொன்னார்"
    ],
    # Full settlement verbs
    "SETTLEMENT_VERBS": [
        "full ah koduthutaaru", "mothamaa mudichitaaru", "clear pannitaaru", "settle aaiduchu",
        "mothama koduthaaru", "muzhumaiyaaga koduthaar", "kanakku mudinjadhu", "all clear",
        "mudichutaaru", "mudichitaaru", "kanakku mudichutaaru", "kanakku mudichuttaar",
        "முழுசா கொடுத்துட்டார்", "மொத்தமா கொடுத்துட்டார்", "கிளியர் பண்ணிட்டார்",
        "செட்டில் ஆயிடுச்சு", "கணக்கு முடிஞ்சது", "முழுத் தொகை செலுத்திவிட்டார்",
        "முழுசா முடிச்சுட்டார்", "முழுசா முடித்தார்", "கணக்கு முடிச்சுட்டார்", "கணக்கை முடித்தார்"
    ],
    # Advance verbs
    "ADVANCE_VERBS": [
        "advance koduthen", "advance koduthaar", "advance anuppinen", "advance", "அட்வான்ஸ்"
    ],
    # Credit sale verbs
    "CREDIT_SALE_VERBS": [
        "sarakku koduthen", "sarakku anuppinen", "porul koduthen", "kadhanuku koduthen", "bill potten",
        "kadhanuku vaanginaar", "kadhanukku vaanginaar", "sarakku kadanuku vaanginaar",
        "சரக்கு கொடுத்தேன்", "சரக்கு அனுப்பினேன்", "பொருள் கொடுத்தேன்", "கடனுக்கு கொடுத்தேன்",
        "சரக்கு கடனுக்கு வாங்கினார்", "கடனுக்கு வாங்கினார்", "சரக்கு வாங்கினார்"
    ],
    # Purchase verbs
    "PURCHASE_VERBS": [
        "sarakku vaanginen", "sarakku vaanginom", "maal vaanginom", "purchase pannen", "stock vaanginom",
        "சரக்கு வாங்கினேன்", "சரக்கு வாங்கினோம்", "பொருள் வாங்கினோம்", "ஸ்டாக் வாங்கினோம்"
    ]
}

# Temporal dictionary for Tamil (offsets in days relative to anchor)
TAMIL_TEMPORAL_LEXICON = {
    "netru": -1, "nethu": -1, "நேற்று": -1, "நேத்து": -1,
    "mundhanal": -2, "munthanallu": -2, "முந்தாநாள்": -2,
    "indru": 0, "iniku": 0, "innaiku": 0, "இன்று": 0, "இன்னைக்கு": 0, "இன்னிக்கு": 0,
    "naalai": 1, "naalaikku": 1, "nalaiku": 1, "நாளை": 1, "நாளைக்கு": 1,
    "naalaikku marunaal": 2, "marunaal": 2, "நாளை மறுநாள்": 2, "மறுநாள்": 2,
    "adutha vaaram": 7, "adutha varam": 7, "அடுத்த வாரம்": 7,
    "kadantha vaaram": -7, "pona vaaram": -7, "கடந்த வாரம்": -7, "போன வாரம்": -7,
    "indha vaaram": 0, "intha vaaram": 0, "இந்த வாரம்": 0,
    "adutha maadham": 30, "adutha masam": 30, "அடுத்த மாதம்": 30, "அடுத்த மாசம்": 30,
    "kadantha maadham": -30, "pona maadham": -30, "போன மாசம்": -30, "கடந்த மாதம்": -30
}

TAMIL_DAYS_OF_WEEK = {
    "thingal": 0, "thingatkilamai": 0, "திங்கள்": 0, "திங்கட்கிழமை": 0,
    "sevvaai": 1, "sevvaikilamai": 1, "செவ்வாய்": 1, "செவ்வாய்க்கிழமை": 1,
    "budhan": 2, "budhankilamai": 2, "புதன்": 2, "புதன்கிழமை": 2,
    "viyazhan": 3, "viyazhakkilamai": 3, "வியாழன்": 3, "வியாழக்கிழமை": 3,
    "velli": 4, "vellikilamai": 4, "வெள்ளி": 4, "வெள்ளிக்கிழமை": 4,
    "sani": 5, "sanikkilamai": 5, "சனி": 5, "சனிக்கிழமை": 5,
    "njaayiru": 6, "njaayitrukilamai": 6, "ஞாயிறு": 6, "ஞாயிற்றுக்கிழமை": 6
}

TAMIL_MONTHS = {
    "ஜனவரி": 1, "பிப்ரவரி": 2, "மார்ச்": 3, "ஏப்ரல்": 4, "மே": 5, "ஜூன்": 6,
    "ஜூலை": 7, "ஆகஸ்ட்": 8, "செப்டம்பர்": 9, "அக்டோபர்": 10, "நவம்பர்": 11, "டிசம்பர்": 12,
    "சித்திரை": 4, "வைகாசி": 5, "ஆனி": 6, "ஆடி": 7, "ஆவணி": 8, "புரட்டாசி": 9,
    "ஐப்பசி": 10, "கார்த்திகை": 11, "மார்கழி": 12, "தை": 1, "மாசி": 2, "பங்குனி": 3
}

TAMIL_HONORIFICS = ["avargal", "anna", "thambi", "aiyya", "bhai", "seth", "sir", "ji", "அவர்கள்", "அண்ணா", "ஐயா", "தம்பி"]

TAMIL_BUSINESS_TERMS = {
    "sarakku": "goods", "porul": "items/goods", "saman": "items", "maligai": "groceries",
    "baki": "outstanding_balance", "baaki": "outstanding_balance", "kadhan": "credit",
    "varavu": "credit_entry", "selavu": "debit_expense", "panam": "money", "kaasu": "money",
    "chillara": "small_cash", "kanakku": "account_ledger", "kurippu": "note"
}
