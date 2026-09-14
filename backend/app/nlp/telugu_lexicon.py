"""
Comprehensive Telugu Financial Lexicon, Grammar Markers, Spoken Numerals, and Vernacular Terms.
Supports Romanized Telugu, Telugu Script (Unicode), and Code-Mixed Transliterations.
"""

from typing import Dict, List, Set

# Telugu Script to Romanized mappings & basic Telugu Unicode range
TELUGU_UNICODE_RANGE = (0x0C00, 0x0C7F)

# Comprehensive Spoken Telugu Digits & Numbers to Integers
TELUGU_NUMERALS: Dict[str, int] = {
    # 0
    "sunna": 0, "sunnam": 0, "zero": 0, "zeero": 0, "జీరో": 0, "సున్నా": 0, "సున్న": 0,
    
    # 1 - 10
    "okati": 1, "oka": 1, "voka": 1, "vokati": 1, "woka": 1, "wokati": 1, "okate": 1, "okkate": 1, "okka": 1, "one": 1, "van": 1, "wan": 1,
    "ఒకటి": 1, "ఒక": 1, "ఒక్కటి": 1, "ఒక్క": 1, "ఒకటే": 1,
    "rendu": 2, "rendo": 2, "randu": 2, "rindu": 2, "two": 2, "too": 2, "tu": 2, "రెండు": 2, "రెండో": 2,
    "mudu": 3, "moodu": 3, "muudu": 3, "mudo": 3, "moodo": 3, "three": 3, "tree": 3, "tri": 3, "thri": 3, "మూడు": 3, "మూడో": 3,
    "nalugu": 4, "naalugu": 4, "nalgu": 4, "naalgu": 4, "nalugo": 4, "naalugo": 4, "four": 4, "for": 4, "phour": 4, "నాలుగు": 4, "నాలుగో": 4, "నలుగు": 4,
    "aidhu": 5, "ayidu": 5, "aidu": 5, "aido": 5, "ayido": 5, "aedhu": 5, "aedu": 5, "five": 5, "faiv": 5, "faive": 5, "ఐదు": 5, "ఐదో": 5,
    "aaru": 6, "aaro": 6, "aaruu": 6, "six": 6, "siks": 6, "sics": 6, "ఆరు": 6, "ఆరో": 6,
    "yedu": 7, "edu": 7, "yeedu": 7, "eedu": 7, "yedo": 7, "edo": 7, "seven": 7, "sevan": 7, "ఏడు": 7, "ఏడో": 7,
    "enimidi": 8, "enmidi": 8, "yenimidi": 8, "yenmidi": 8, "enimidho": 8, "eight": 8, "eyt": 8, "ait": 8, "aight": 8, "ఎనిమిది": 8, "ఎనిమిదో": 8,
    "thommidi": 9, "tommidi": 9, "thomdi": 9, "tomdi": 9, "thommidho": 9, "tommidho": 9, "nine": 9, "nain": 9, "తొమ్మిది": 9, "తొమ్మిదో": 9,
    "padi": 10, "padhi": 10, "ten": 10, "పది": 10,
    
    # 11 - 19
    "padakondu": 11, "padakondoo": 11, "eleven": 11, "elevan": 11, "పదకొండు": 11,
    "pannendu": 12, "panendu": 12, "twelve": 12, "twelv": 12, "పన్నెండు": 12,
    "padhamudu": 13, "padamudu": 13, "padhamoodu": 13, "padamoodu": 13, "thirteen": 13, "therteen": 13, "పదమూడు": 13,
    "padhanalugu": 14, "padanalugu": 14, "padhanaalugu": 14, "padnaalugu": 14, "fourteen": 14, "forteen": 14, "పద్నాలుగు": 14,
    "padhaidhu": 15, "padhayidu": 15, "padhaidu": 15, "padihenu": 15, "padhihenu": 15, "padiheynu": 15, "fifteen": 15, "fiftin": 15, "పదిహేను": 15,
    "padahaaru": 16, "padaharu": 16, "sixteen": 16, "sikstin": 16, "పదహారు": 16,
    "padhaedu": 17, "padhayedu": 17, "padihedu": 17, "padhihedu": 17, "seventeen": 17, "seventin": 17, "పదిహేడు": 17,
    "padhenimidi": 18, "padenimidi": 18, "eighteen": 18, "eightin": 18, "పద్దెనిమిది": 18,
    "pantommidi": 19, "pantomidi": 19, "nineteen": 19, "ninetin": 19, "పంతొమ్మిది": 19,
    
    # 20 - 90 (Tens)
    "iravai": 20, "iruvai": 20, "eeravai": 20, "iravayy": 20, "iravay": 20, "twenty": 20, "twenti": 20, "twanti": 20, "ఇరవై": 20,
    "muppai": 30, "mupphai": 30, "mupai": 30, "muppay": 30, "thirty": 30, "therty": 30, "ముప్పై": 30,
    "nalabhai": 40, "nalabai": 40, "naalabhai": 40, "naalabai": 40, "nalubhai": 40, "nalbhai": 40, "forty": 40, "fourty": 40, "నలభై": 40,
    "yaabhai": 50, "yabhai": 50, "eabhai": 50, "yabhay": 50, "yaabay": 50, "fifty": 50, "fifti": 50, "యాభై": 50,
    "aravai": 60, "aruvai": 60, "aaravai": 60, "aravay": 60, "sixty": 60, "siksti": 60, "అరవై": 60,
    "debbai": 70, "debbhai": 70, "debay": 70, "debhai": 70, "seventy": 70, "seventi": 70, "డెబ్బై": 70,
    "enabhai": 80, "enabai": 80, "yenabhai": 80, "yenabai": 80, "enabay": 80, "enbhai": 80, "eighty": 80, "eyti": 80, "ఎనభై": 80,
    "thombhai": 90, "tombai": 90, "thombal": 90, "tombaai": 90, "tombhai": 90, "tombay": 90, "ninety": 90, "nineti": 90, "niniti": 90, "తొంభై": 90,
    
    # Common Fused Compounds (Tens + Units)
    "iravayokati": 21, "iravaiyokati": 21, "iravayrendu": 22, "iravaymudu": 23, "iravaynalugu": 24,
    "iravayaidhu": 25, "iravayidu": 25, "iravayaaru": 26, "iravayyedu": 27, "iravayenimidi": 28, "iravaythommidi": 29,
    "muppayaidhu": 35, "muppayidu": 35, "nalabhayaidhu": 45, "nalabhayidu": 45, "yaabhayaidhu": 55, "yaabhayidu": 55,
    "aravayaidhu": 65, "debbayaidhu": 75, "enabhayaidhu": 85, "thombhayaidhu": 95,
    "ఇరవైఒకటి": 21, "ఇరవైరెండు": 22, "ఇరవైమూడు": 23, "ఇరవైనాలుగు": 24, "ఇరవైఐదు": 25,
    "ముప్పైఐదు": 35, "నలభైఐదు": 45, "యాభైఐదు": 55, "డెబ్బైఐదు": 75,

    # Hundreds (100 - 900)
    "vanda": 100, "vandha": 100, "wanda": 100, "wandha": 100, "nooru": 100, "nuru": 100, "noorlu": 100, "nuri": 100,
    "vandalu": 100, "vandhalu": 100, "wandalu": 100, "wandhalu": 100, "vandala": 100, "vandhala": 100, "wandala": 100, "wandhala": 100,
    "hundred": 100, "hundreds": 100, "hunderd": 100, "hunderds": 100, "hondred": 100, "hondreds": 100,
    "hundered": 100, "hundread": 100, "handred": 100, "handrad": 100, "hundard": 100, "hndrd": 100, "hund": 100,
    "వంద": 100, "నూరు": 100, "వందలు": 100, "వందల": 100,
    "innuru": 200, "rendu vandalu": 200, "renduvandala": 200, "renduvandalu": 200, "rendu vandala": 200, "రెండు వందలు": 200, "రెండువందల": 200, "రెండువందలు": 200, "ఇన్నూరు": 200, "రెండు వందల": 200,
    "munnuru": 300, "moodu vandalu": 300, "mooduvandala": 300, "mooduvandalu": 300, "moodu vandala": 300, "మూడు వందలు": 300, "మూడువందల": 300, "మూడువందలు": 300, "మున్నూరు": 300, "మూడు వందల": 300,
    "nanuru": 400, "naalugu vandalu": 400, "naaluguvandala": 400, "nalugu vandalu": 400, "నాలుగు వందలు": 400, "నాలుగువందల": 400, "నాలుగువందలు": 400, "నానూరు": 400, "నాలుగు వందల": 400,
    "enuru": 500, "aidhu vandalu": 500, "aiduvandalu": 500, "aiduvandala": 500, "aidu vandalu": 500, "aidhu vandala": 500, "ఐదు వందలు": 500, "ఐదువందల": 500, "ఐదువందలు": 500, "ఐనూరు": 500, "ఐదు వందల": 500,
    "aaru vandalu": 600, "aaruvandala": 600, "aaruvandalu": 600, "aaru vandala": 600, "ఆరు వందలు": 600, "ఆరువందల": 600, "ఆరువందలు": 600, "ఆరు వందల": 600,
    "eedu vandalu": 700, "eeduvandala": 700, "edu vandalu": 700, "eedu vandala": 700, "ఏడు వందలు": 700, "ఏడువందల": 700, "ఏడువందలు": 700, "ఏడు వందల": 700,
    "enimidi vandalu": 800, "enimidivandala": 800, "enimidi vandala": 800, "ఎనిమిది వందలు": 800, "ఎనిమిదివందల": 800, "ఎనిమిదివందలు": 800, "ఎనిమిది వందల": 800,
    "tommidi vandalu": 900, "tommidivandala": 900, "tommidi vandala": 900, "తొమ్మిది వందలు": 900, "తొమ్మిదివందల": 900, "తొమ్మిదివందలు": 900, "తొమ్మిది వందల": 900,

    # Thousands (Indian Accent, Vernacular & Romanized Telugu)
    "veyyi": 1000, "veye": 1000, "vei": 1000, "vela": 1000, "vele": 1000, "velu": 1000, "veyla": 1000, "veylu": 1000, "veela": 1000, "veelu": 1000, "veyyee": 1000, "veyalu": 1000, "veyyalu": 1000,
    "thousand": 1000, "thousands": 1000, "thouzad": 1000, "thouzand": 1000, "thoujand": 1000, "thoujan": 1000,
    "thousend": 1000, "thousan": 1000, "thowsand": 1000, "thowzand": 1000, "thowjand": 1000,
    "towjand": 1000, "taujand": 1000, "tauzand": 1000, "tauzan": 1000, "tozand": 1000, "towzand": 1000, "tozhand": 1000,
    "thojand": 1000, "thozand": 1000, "thozhand": 1000, "tawzand": 1000, "tawjand": 1000,
    "thousad": 1000, "thousen": 1000, "thousant": 1000, "thouzant": 1000, "thousnd": 1000, "thznd": 1000, "thsn": 1000,
    "k": 1000,
    "వేయి": 1000, "వెయ్యి": 1000, "వేల": 1000, "వేలు": 1000, "వేయ్": 1000, "వేయిల": 1000, "వేలా": 1000,

    # Thousands & Fused Compounds (1,000 - 99,000)
    "rendu vela": 2000, "renduvela": 2000, "rendu velu": 2000, "renduvelu": 2000, "rendu veyyi": 2000,
    "రెండు వేలు": 2000, "రెండువేలు": 2000, "రెండువేల": 2000, "రెండు వేల": 2000, "రెండు వేయి": 2000, "రెండువెయ్యి": 2000,
    "moodu vela": 3000, "mooduvela": 3000, "moodu velu": 3000, "mooduvelu": 3000,
    "మూడు వేలు": 3000, "మూడువేలు": 3000, "మూడువేల": 3000, "మూడు వేల": 3000, "మూడు వేయి": 3000,
    "naalugu vela": 4000, "naaluguvela": 4000, "nalugu vela": 4000, "naluguvela": 4000,
    "నాలుగు వేలు": 4000, "నాలుగువేలు": 4000, "నాలుగువేల": 4000, "నాలుగు వేల": 4000,
    "aidhu vela": 5000, "aiduvela": 5000, "aidu vela": 5000, "aidhuvela": 5000, "aidhu velu": 5000, "aiduvelu": 5000,
    "ఐదు వేలు": 5000, "ఐదువేలు": 5000, "ఐదువేల": 5000, "ఐదు వేల": 5000, "ఐదు వేయి": 5000,
    "aaru vela": 6000, "aaruvela": 6000, "aaru velu": 6000, "aaruvelu": 6000,
    "ఆరు వేలు": 6000, "ఆరువేలు": 6000, "ఆరువేల": 6000, "ఆరు వేల": 6000,
    "eedu vela": 7000, "eeduvela": 7000, "edu vela": 7000, "eduvela": 7000,
    "ఏడు వేలు": 7000, "ఏడువేలు": 7000, "ఏడువేల": 7000, "ఏడు వేల": 7000,
    "enimidi vela": 8000, "enimidivela": 8000, "enimidi velu": 8000,
    "ఎనిమిది వేలు": 8000, "ఎనిమిదివేలు": 8000, "ఎనిమిదివేల": 8000, "ఎనిమిది వేల": 8000,
    "tommidi vela": 9000, "tommidivela": 9000, "tommidi velu": 9000,
    "తొమ్మిది వేలు": 9000, "తొమ్మిదివేలు": 9000, "తొమ్మిదివేల": 9000, "తొమ్మిది వేల": 9000,

    # Tens + Thousands (10,000 - 90,000)
    "padivela": 10000, "padhivelu": 10000, "padi vela": 10000, "padhi vela": 10000, "padi velu": 10000,
    "పది వేలు": 10000, "పదివేలు": 10000, "పదివేల": 10000, "పది వేల": 10000,
    "padihenu vela": 15000, "padihenuvela": 15000, "పదిహేను వేలు": 15000, "పదిహేనువేల": 15000, "పదిహేను వేల": 15000,
    "iravaivela": 20000, "iravaivelu": 20000, "iravai vela": 20000, "iravai velu": 20000,
    "ఇరవై వేలు": 20000, "ఇరవైవేలు": 20000, "ఇరవైవేల": 20000, "ఇరవై వేల": 20000,
    "iravayaidhu vela": 25000, "iravai aidu vela": 25000, "ఇరవై ఐదు వేలు": 25000, "ఇరవైఐదువేల": 25000,
    "muppaivela": 30000, "muppaivelu": 30000, "muppai vela": 30000,
    "ముప్పై వేలు": 30000, "ముప్పైవేలు": 30000, "ముప్పైవేల": 30000, "ముప్పై వేల": 30000,
    "nalabhaivela": 40000, "nalabhaivelu": 40000, "nalabhai vela": 40000,
    "నలభై వేలు": 40000, "నలభైవేలు": 40000, "నలభైవేల": 40000, "నలభై వేల": 40000,
    "yaabhaivela": 50000, "yaabhaivelu": 50000, "yaabhai vela": 50000, "yabhai vela": 50000,
    "యాభై వేలు": 50000, "యాభైవేలు": 50000, "యాభైవేల": 50000, "యాభై వేల": 50000,
    "aravaivela": 60000, "aravaivelu": 60000, "aravai vela": 60000,
    "అరవై వేలు": 60000, "అరవైవేలు": 60000, "అరవైవేల": 60000, "అరవై వేల": 60000,
    "debbaivela": 70000, "debbaivelu": 70000, "debbai vela": 70000,
    "డెబ్బై వేలు": 70000, "డెబ్బైవేలు": 70000, "డెబ్బైవేల": 70000, "డెబ్బై వేల": 70000,
    "enabhaivela": 80000, "enabhaivelu": 80000, "enabhai vela": 80000,
    "ఎనభై వేలు": 80000, "ఎనభైవేలు": 80000, "ఎనభైవేల": 80000, "ఎనభై వేల": 80000,
    "thombhaivela": 90000, "thombhaivelu": 90000, "thombhai vela": 90000,
    "తొంభై వేలు": 90000, "తొంభైవేలు": 90000, "తొంభైవేల": 90000, "తొంభై వేల": 90000,
    
    # Lakhs (Indian English & Vernacular)
    "laksha": 100000, "lakshalu": 100000, "lakshala": 100000, "lakh": 100000, "lakhs": 100000,
    "lac": 100000, "lacs": 100000, "lakha": 100000, "lakhas": 100000, "laakh": 100000, "laakhs": 100000, "laak": 100000, "laaks": 100000,
    "lack": 100000, "lacks": 100000, "lahk": 100000, "lahks": 100000, "lax": 100000, "laksh": 100000, "laksham": 100000,
    "rendu lakshalu": 200000, "rendu laksha": 200000, "aidu lakshalu": 500000, "padi lakshalu": 1000000,
    "లక్ష": 100000, "లక్షలు": 100000, "లక్షల": 100000, "రెండు లక్షలు": 200000, "రెండు లక్షల": 200000, "ఐదు లక్షలు": 500000, "పది లక్షలు": 1000000, "యాభై లక్షలు": 5000000,
    
    # Crores
    "koti": 10000000, "kotlu": 10000000, "kotla": 10000000, "kotee": 10000000,
    "crore": 10000000, "crores": 10000000, "cror": 10000000, "crors": 10000000,
    "krore": 10000000, "krores": 10000000, "kror": 10000000, "krors": 10000000, "cr": 10000000, "crs": 10000000,
    "rendu kotlu": 20000000, "aidu kotlu": 50000000,
    "కోటి": 10000000, "కోట్లు": 10000000, "కోట్ల": 10000000, "రెండు కోట్లు": 20000000, "ఐదు కోట్లు": 50000000,
}

# Postpositions & Directional markers
DIRECTION_MARKERS = {
    # Postpositions that attach to counterparties we are paying TO (Supplier / Outflow)
    "PAYABLE_POSTPOSITIONS": [
        "ki", "ku", "kante", "vaadiki", "athaniki", "aameku", "వారికి", "కి", "కు",
        "gariki", "annaki", "bhaiki", "sethki", "గారికి", "అన్నకి", "to", "pay to", "due to", "give to", "paid to",
        "transferred to", "sent to", "gave to", "payable to"
    ],
    # Postpositions that attach to counterparties we are receiving FROM (Customer / Inflow)
    "RECEIVABLE_POSTPOSITIONS": [
        "nundi", "nunchi", "daggara", "daggarnundi", "daggara nundi", "daggara nunchi", "vadda", "vadda nundi", "nuṇḍi", "nuñci",
        "నుండి", "నుంచి", "దగ్గర", "దగ్గర నుండి", "దగ్గర్నుండి", "వద్ద", "వద్ద నుండి", "తో",
        "from", "due from", "received from", "collected from", "got from", "by"
    ],
    
    # Obligation / Future / Due Payable (Business has to pay supplier)
    "PAYABLE_VERBS": [
        "ivvali", "ivvaali", "ivaali", "ivali", "ivvalsi", "ivvalsindi", "ivvalasindi", "chellinchali", "chellinchalsindi",
        "kattali", "kattaali", "kattalsindi", "kattalira", "ivvalira", "ivaalira", "evali", "evvali", "eeyali", "eeyyali",
        "pay cheyyali", "pay cheyali", "ivvanundi", "need to pay", "have to pay", "payable", "owe", "owes",
        "pay", "pay to", "give", "give to", "transfer cheyyali", "transfer cheyali", "gpay cheyyali", "send cheyyali",
        "ఇవ్వాలి", "ఇవ్వాల్సింది", "ఇవ్వాల్సి ఉంది", "ఇవ్వవలసి ఉంది", "చెల్లించాలి", "చెల్లించాల్సింది", "కట్టాలి", "కట్టాల్సింది", "కట్టాల్సి ఉంది"
    ],
    
    # Obligation / Due Receivable (Customer has to pay business / Asset)
    "RECEIVABLE_VERBS": [
        "ravali", "raavali", "ravalsi", "ravalsindi", "ravalsi undi", "ravalasi undi", "teesukovali", "teeskovali", "theeskovali",
        "vasool cheyyali", "vasul cheyali", "vasool cheyali", "collect cheyyali", "collect cheyali", "collect",
        "pending undi", "pending", "baki undi", "baaki undi", "baki unnadu", "baaki unnadu", "baki unnadi", "baaki unnadi",
        "baki", "baaki", "ravanundi", "receivable", "due undi", "due from", "receivable from", "to receive", "to collect",
        "customer ivvali", "client ivvali", "customer ivvaali", "inflow",
        "రావాలి", "రావాల్సి ఉంది", "రావలసి ఉంది", "రావాలంట", "రావలసినది", "రావాల్సింది",
        "బాకీ ఉంది", "బాకీ ఉన్నాడు", "బాకీ ఉన్నది", "బాకీ",
        "పెండింగ్ ఉంది", "పెండింగ్", "తీసుకోవాలి", "వసూలు చేయాలి", "వసూలు", "కలెక్ట్ చేయాలి", "కలెక్ట్", "డ్యూ ఉంది", "డ్యూ"
    ],
    
    # 3rd Person Past & Inflow Verbs (Customer paid business - reducing receivable balance, increasing cash inflow)
    "PAID_BY_CUSTOMER_VERBS": [
        "ichadu", "ichindi", "icharu", "ichesadu", "icheysadu", "ichesthadu", "ichesindi", "ichessaru", "ichharu",
        "pampadu", "pampindi", "pamparu", "pampesadu", "pampinchadu", "pampinchesadu",
        "kattadu", "kattindi", "kattaru", "kattesadu", "kattesindi", "kattesaru",
        "chellinchadu", "chellinchindi", "chellincharu", "chellinchesadu",
        "vachindi", "vachindhi", "vachayi", "vacchesindi", "vacchindi", "andindi", "cherindi",
        "transfer chesadu", "transfer chesindi", "transfer chesaru", "pay chesadu", "pay chesindi", "pay chesaru",
        "gpay chesadu", "phonepe chesadu", "settle chesadu", "upi chesadu", "clear chesadu", "deposit chesadu", "deposited",
        "received", "received from", "collected from", "got from", "paid by", "sent by", "transferred by",
        "ఇచ్చాడు", "ఇచ్చింది", "ఇచ్చారు", "ఇచ్చేశాడు", "ఇచ్చేసాడు", "ఇచ్చేశారు", "ఇచ్చేసింది",
        "కట్టాడు", "కట్టింది", "కట్టారు", "కట్టేశాడు", "కట్టేసాడు", "కట్టేశారు", "కట్టేసింది",
        "చెల్లించాడు", "చెల్లించింది", "చెల్లించారు", "చెల్లించేశాడు", "చెల్లించేశారు",
        "వచ్చింది", "వచ్చాయి", "అందింది", "చేరింది",
        "పంపాడు", "పంపింది", "పంపారు", "పంపించేశాడు", "పంపించాడు",
        "ట్రాన్స్ఫర్ చేశాడు", "ట్రాన్స్ఫర్ చేసింది", "ట్రాన్స్ఫర్ చేశారు", "పే చేశాడు", "పే చేసింది", "పే చేశారు",
        "గూగుల్ పే చేశాడు", "ఫోన్ పే చేశాడు", "క్లియర్ చేశాడు", "సెటిల్ చేశాడు"
    ],
    
    # 1st Person Past Verbs (Business paid supplier - reducing payable balance, increasing cash outflow)
    "PAID_BY_BUSINESS_VERBS": [
        "ichanu", "icha", "ichesa", "ichesanu", "icheysa", "icheysanu", "ichestha", "ichamu", "icham",
        "pampanu", "pampa", "pampesa", "pampesanu", "pampeysa", "pampamu", "pampam",
        "kattanu", "katta", "kattesa", "kattesanu", "katteysa", "kattinam", "kattamu", "kattam",
        "chellincha", "chellinchanu", "chellincham",
        "transfer chesa", "transfer chesanu", "pay chesa", "pay chesanu", "gpay chesa", "phonepe chesa", "settle chesa", "settle chesanu", "upi chesa",
        "paid to", "transferred to", "gave to", "sent to", "deposit chesam", "deposited to",
        "ఇచ్చాను", "ఇచ్చా", "ఇచ్చేశాను", "ఇచ్చేశాం", "ఇచ్చాము", "ఇచ్చాం",
        "కట్టాను", "కట్టా", "కట్టేసా", "కట్టేశాను", "కట్టాము", "కట్టేశాం",
        "చెల్లించాను", "చెల్లించాం",
        "పంపాను", "పంపాం", "పంపేశాను", "పంపేశాం", "ట్రాన్స్ఫర్ చేశాం", "ట్రాన్స్ఫర్ చేశాను", "పే చేశాం", "పే చేశాను"
    ],
    
    "PROMISE_VERBS": [
        "istanu annadu", "istha annadu", "isthadu annadu", "pay chestha annadu", "transfer chestha annadu",
        "clear chestha annadu", "settle chestha annadu", "pampistha annadu", "ivvagalanu annadu",
        "istanu ani cheppadu", "isthanannadu", "isthannadu", "ఇస్తాను అన్నాడు", "ఇస్తానన్నాడు", "చెల్లిస్తాను అన్నాడు"
    ],
    
    "SETTLEMENT_VERBS": [
        "complete ga ichesadu", "motham ichesadu", "mottham ichesadu", "clear chesesadu", "settle aipoindi", "full payment chesadu",
        "mottham dabbulu ichesadu", "motham dabbulu ichesadu", "dabbulu mottham ichesadu", "dabbulu ichesadu",
        "mottham ichesindi", "motham ichesindi", "complete payment", "zero aipoindi", "all clear",
        "మొత్తం ఇచ్చేశాడు", "మొత్తం డబ్బులు ఇచ్చేశాడు", "క్లియర్ అయిపోయింది", "మొత్తం కట్టేశాడు"
    ],
    
    "ADVANCE_VERBS": [
        "advance icha", "advance ichadu", "advance transfer", "advance ga", "advance", "అడ్వాన్స్"
    ],
    
    "CREDIT_SALE_VERBS": [
        "saraku icha", "maal ichanu", "goods icha", "credit meeda icha", "udhari icha", "bill generate chesa",
        "సరకు ఇచ్చా", "ఉధారి ఇచ్చా"
    ],
    
    "PURCHASE_VERBS": [
        "saraku konna", "maal konnam", "stock theppincham", "purchase chesam", "కొన్నాం", "స్టాక్ తెప్పించాం"
    ]
}

# Temporal dictionary & relative offsets (in days relative to anchor)
TEMPORAL_LEXICON = {
    "ninna": -1, "yesterday": -1, "నిన్న": -1,
    "monna": -2, "day before yesterday": -2, "మొన్న": -2,
    "ee roju": 0, "today": 0, "eroju": 0, "ఈ రోజు": 0, "నేడు": 0, "nedu": 0,
    "repu": 1, "tomorrow": 1, "రేపు": 1,
    "ellundi": 2, "day after tomorrow": 2, "ఎల్లుండి": 2,
    "vache vaaram": 7, "next week": 7, "వచ్చే వారం": 7,
    "kritham vaaram": -7, "last week": -7, "పోయిన వారం": -7,
    "ee vaaram": 0, "this week": 0, "ఈ వారం": 0,
    "vache nela": 30, "next month": 30, "వచ్చే నెల": 30,
    "kritham nela": -30, "last month": -30, "పోయిన నెల": -30,
    "last 3 months": -90,
}

DAYS_OF_WEEK = {
    "somavaram": 0, "monday": 0, "సోమవారం": 0,
    "mangalavaram": 1, "tuesday": 1, "మంగళవారం": 1,
    "budhavaram": 2, "wednesday": 2, "బుధవారం": 2,
    "guruvaram": 3, "thursday": 3, "గురువారం": 3,
    "sukravaram": 4, "friday": 4, "శుక్రవారం": 4,
    "sanivaram": 5, "saturday": 5, "శనివారం": 5,
    "aadivaram": 6, "sunday": 6, "ఆదివారం": 6,
}

TELUGU_MONTHS = {
    # Telugu Script
    "జనవరి": 1, "ఫిబ్రవరి": 2, "మార్చి": 3, "ఏప్రిల్": 4, "మే": 5, "జూన్": 6,
    "జూలై": 7, "ఆగస్టు": 8, "ఆగష్టు": 8, "సెప్టెంబర్": 9, "సెప్టెంబరు": 9,
    "అక్టోబర్": 10, "అక్టోబరు": 10, "నవంబర్": 11, "నవంబరు": 11, "డిసెంబర్": 12, "డిసెంబరు": 12,
    
    # English / Romanized
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6,
    "july": 7, "jul": 7, "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12
}

# Honorifics and suffixes
TELUGU_HONORIFICS = ["garu", "anna", "bhai", "reddy", "rao", "seth", "saab", "sir", "ji", "gaaru", "గారు", "అన్నా"]

# Payment Methods
PAYMENT_METHODS = {
    "cash": ["cash", "nagadu", "chethi lo", "చేతిలో", "నగదు"],
    "upi": ["upi", "gpay", "google pay", "phonepe", "paytm", "phone pe", "యుపిఐ"],
    "bank_transfer": ["bank transfer", "neft", "rtgs", "imps", "account transfer", "bank", "ఖాతా"],
    "cheque": ["cheque", "check", "చెక్"]
}

# Vernacular Trade & Business Terms
BUSINESS_TERMS = {
    "saraku": "goods", "maal": "goods", "saman": "items", "kirana": "groceries",
    "baki": "outstanding_balance", "udhari": "credit", "jama": "credit_entry",
    "kharchu": "debit_expense", "dabbulu": "money", "chillara": "change/small_cash",
    "kachha": "unbilled/provisional", "pakka": "formal_tax_invoice", "khata": "account_ledger"
}
