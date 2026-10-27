"""
Synthetic & Gold Multi-Lingual Dataset Generator for Telugu, Tamil, Hindi & English Financial NLP.
Generates comprehensive dedicated corpuses for Tamil and Hindi, as well as multi-lingual test sets.
"""

import json
import random
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

random.seed(42)

DATASET_DIR = Path(__file__).resolve().parent
os.makedirs(DATASET_DIR, exist_ok=True)

# ----------------- TELUGU DATA DEFINITIONS -----------------
TELUGU_ACTORS = ["Ramesh", "Suresh", "Mahesh", "Venkat", "Lakshmi", "Priya", "Rajesh", "Krishna", "Ravi", "Anand", "Naresh", "Kiran", "Satish", "Srinivas", "Balu"]
TELUGU_SCRIPT_ACTORS = ["రమేష్", "సురేష్", "మహేష్", "వెంకట్", "లక్ష్మి ట్రేడర్స్", "ప్రియ మెడికల్స్", "రాజేష్", "కృష్ణ కిరాణా", "రవి", "ఆనంద్"]
TELUGU_HONORIFICS = ["", " garu", " anna", " gaaru", " bhai", " akka"]

TELUGU_SPOKEN_NUMS = [
    (100, "vanda"), (200, "rendu vandalu"), (500, "aidhu vandalu"), (1000, "veyyi"),
    (1500, "veyyi aidhu vandalu"), (2000, "rendu vela"), (2500, "rendu vela five hundred"),
    (3000, "mudu vela"), (5000, "aidhu vela"), (10000, "padhi vela"), (15000, "padhaidhu vela"),
    (20000, "iravai vela"), (25000, "iravai aidhu vela"), (40000, "nalabhai vela"),
    (50000, "yaabhai vela"), (100000, "oka laksha")
]

# ----------------- TAMIL DATA DEFINITIONS -----------------
TAMIL_ACTORS = ["Murugan", "Selvam", "Kavitha", "Senthil", "Karthik", "Praveen", "Meena", "Vignesh", "Anbarasan", "Saravanan", "Ganesh", "Dinesh", "Kannan"]
TAMIL_SCRIPT_ACTORS = ["முருகன்", "செல்வம்", "கவிதா", "செந்தில்", "கார்த்திக்", "பிரவீன்", "மீனா", "விக்னேஷ்", "சரவணன்", "கண்ணன்"]
TAMIL_HONORIFICS = ["", " avargal", " anna", " aiyya", " thambi", " bhai"]

TAMIL_SPOKEN_NUMS = [
    (100, "nooru"), (200, "irunooru"), (300, "munnooru"), (400, "naanooru"),
    (500, "ainooru"), (500, "anju nooru"), (600, "aranooru"), (1000, "aayiram"),
    (1500, "aayirathu ainooru"), (2000, "irandaayiram"), (2000, "rendaayiram"),
    (2500, "rendaayirathu ainooru"), (3000, "moovaayiram"), (4000, "naalaayiram"),
    (5000, "aiyyaayiram"), (5000, "anjaayiram"), (8000, "ettaayiram"), (10000, "patthaayiram"),
    (15000, "pathinanjaayiram"), (20000, "irubadhaayiram"), (25000, "irubathaindhaayiram"),
    (40000, "naarpathaayiram"), (50000, "aimbadhaayiram"), (50000, "ambadhaayiram"),
    (100000, "oru latcham")
]

TAMIL_TEMPORAL_PHRASES = [
    ("netru", "EVENT_DATE", -1),
    ("nethu", "EVENT_DATE", -1),
    ("indru", "EVENT_DATE", 0),
    ("iniku", "EVENT_DATE", 0),
    ("naalai", "DUE_DATE", 1),
    ("naalaikku", "DUE_DATE", 1),
    ("velli kilamai kku", "DUE_DATE", 4),
    ("adutha vaaram", "DUE_DATE", 7),
    ("pona vaaram", "EVENT_DATE", -7),
    ("adutha maadham", "DUE_DATE", 30),
    ("pona maasam", "EVENT_DATE", -30)
]

# ----------------- HINDI DATA DEFINITIONS -----------------
HINDI_ACTORS = ["Rahul", "Amit", "Vikram", "Rohit", "Pooja", "Sunil", "Manoj", "Ajay", "Deepak", "Rakesh", "Sanjay", "Rajeev", "Vikas"]
HINDI_SCRIPT_ACTORS = ["राहुल", "अमित", "विक्रम", "रोहित", "पूजा", "सुनील", "मनोज", "अजय", "दीपक", "राकेश", "संजय", "राजीव"]
HINDI_HONORIFICS = ["", " ji", " bhaiya", " bhai", " sethji", " saab"]

HINDI_SPOKEN_NUMS = [
    (100, "ek sau"), (200, "do sau"), (300, "teen sau"), (400, "chaar sau"),
    (500, "paanch sau"), (600, "chhe sau"), (1000, "ek hazaar"), (1500, "dedh hazaar"),
    (2000, "do hazaar"), (2500, "dhai hazaar"), (3000, "teen hazaar"), (4000, "chaar hazaar"),
    (5000, "paanch hazaar"), (8000, "aath hazaar"), (10000, "das hazaar"), (15000, "pandrah hazaar"),
    (20000, "bees hazaar"), (25000, "pachees hazaar"), (30000, "tees hazaar"), (40000, "chalis hazaar"),
    (50000, "pachaas hazaar"), (100000, "ek lakh")
]

HINDI_TEMPORAL_PHRASES = [
    ("kal", "EVENT_DATE", -1),
    ("aaj", "EVENT_DATE", 0),
    ("parson", "DUE_DATE", 2),
    ("agle hafte", "DUE_DATE", 7),
    ("pichle hafte", "EVENT_DATE", -7),
    ("shukrawar ko", "DUE_DATE", 4),
    ("agle mahine", "DUE_DATE", 30),
    ("pichle mahine", "EVENT_DATE", -30)
]


def generate_tamil_corpus() -> list:
    """Generates >2,000 realistic, domain-accurate financial bookkeeping sentences in Tamil."""
    samples = []
    
    # 1. Spoken Tamil Numerals & Tanglish (e.g. 'Murugan ainooru tharanum adutha vaaram')
    for _ in range(600):
        actor = random.choice(TAMIL_ACTORS) + random.choice(TAMIL_HONORIFICS)
        amount_num, amount_spoken = random.choice(TAMIL_SPOKEN_NUMS)
        temp_phrase, role, offset = random.choice(TAMIL_TEMPORAL_PHRASES)
        
        templates = [
            (f"{actor} {amount_spoken} tharanum {temp_phrase}", "receivable", "payment_commitment" if role == "DUE_DATE" else "receivable_obligation"),
            (f"{actor} {temp_phrase} {amount_spoken} koduthaar", "receivable", "partial_payment"),
            (f"Supplier kku {amount_spoken} kodukanum {temp_phrase}", "payable", "payable_obligation"),
            (f"{actor} kitterundhu {amount_spoken} varanum", "receivable", "receivable_invoice"),
            (f"{actor} {temp_phrase} kku {amount_spoken} tharen nu sonnaar", "receivable", "payment_commitment"),
            (f"{actor} kku {amount_spoken} advance anuppinen", "payable", "advance_payment")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language": "tamil",
            "category": "spoken_tamil_numerals",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor.strip(),
                "amount": amount_num,
                "direction": direction,
                "event_type": event_type,
                "temporal_role": role
            }
        })

    # 2. Pure Tamil Script Category (e.g. 'முருகன் ₹2500 பாக்கி உள்ளது')
    for _ in range(600):
        actor = random.choice(TAMIL_SCRIPT_ACTORS)
        amount = random.choice([500, 1000, 1500, 2000, 2500, 3000, 5000, 8000, 10000, 25000])
        templates = [
            (f"{actor} இடம் {amount} பாக்கி இருக்கு", "receivable", "receivable_invoice"),
            (f"{actor} நேற்று {amount} கொடுத்தார்", "receivable", "partial_payment"),
            (f"சப்ளையருக்கு {amount} தர வேண்டும்", "payable", "payable_obligation"),
            (f"{actor} வெள்ளிக்கிழமை {amount} தருவேன்னு சொன்னார்", "receivable", "payment_commitment"),
            (f"{actor} க்கு {amount} அட்வான்ஸ் அனுப்பினோம்", "payable", "advance_payment"),
            (f"{actor} சரக்கு கடனுக்கு வாங்கினார் {amount}", "receivable", "credit_sale"),
            (f"{actor} கணக்கு முழுசா முடிச்சுட்டார்", "receivable", "full_settlement", 0)
        ]
        chosen = random.choice(templates)
        text = chosen[0]
        direction = chosen[1]
        event_type = chosen[2]
        amt_val = chosen[3] if len(chosen) > 3 else amount
        
        samples.append({
            "text": text,
            "language": "tamil",
            "category": "tamil_script",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor,
                "amount": amt_val,
                "direction": direction,
                "event_type": event_type
            }
        })

    # 3. Tanglish / Code-Mixed Tamil-English (e.g. 'Kavitha ku 1500 pending irukku, UPI pannaar')
    for _ in range(500):
        actor = random.choice(TAMIL_ACTORS) + random.choice(TAMIL_HONORIFICS)
        amount = random.choice([750, 1200, 2000, 2500, 3500, 4800, 5000, 8000, 12000, 25000])
        method = random.choice(["cash", "online", "gpay", "phonepe", "bank transfer"])
        
        templates = [
            (f"{actor} kku {amount} pending irukku", "receivable", "receivable_invoice"),
            (f"{actor} netru {amount} {method} moolam koduthaar", "receivable", "partial_payment"),
            (f"Supplier kku {amount} pay pannanum", "payable", "payable_obligation"),
            (f"{actor} kitta irundhu {amount} varanum", "receivable", "receivable_invoice"),
            (f"{actor} Friday kku {amount} pay panren nu sonnaar", "receivable", "payment_commitment"),
            (f"{actor} full ah clear pannitaaru", "receivable", "full_settlement", 0)
        ]
        chosen = random.choice(templates)
        text = chosen[0]
        direction = chosen[1]
        event_type = chosen[2]
        amt_val = chosen[3] if len(chosen) > 3 else amount
        
        samples.append({
            "text": text,
            "language": "tamil",
            "category": "code_mixed_tanglish",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor.strip(),
                "amount": amt_val,
                "direction": direction,
                "event_type": event_type
            }
        })

    # 4. Tamil Analytical Financial Queries (e.g. 'யார் அதிகம் தர வேண்டும்', 'suppliers ku evalo tharanum')
    tamil_queries = [
        ("yaar athigam tharanum", "TOP_DEBTORS", "customers"),
        ("யார் அதிகம் தர வேண்டும்", "TOP_DEBTORS", "customers"),
        ("suppliers ku evalo tharanum", "TOTAL_PAYABLES", "suppliers"),
        ("சப்ளையர்களுக்கு எவ்வளவு தர வேண்டும்", "TOTAL_PAYABLES", "suppliers"),
        ("customers kitterundhu evalo varanum", "TOTAL_RECEIVABLES", "customers"),
        ("கஸ்டமர்களிடம் எவ்வளவு வர வேண்டும்", "TOTAL_RECEIVABLES", "customers"),
        ("adutha vaaram payments enna", "UPCOMING_PAYMENTS", "payment_commitments"),
        ("velli payments enna", "UPCOMING_PAYMENTS", "payment_commitments"),
        ("overdue customers yaar", "OVERDUE_CUSTOMERS", "customers")
    ]
    for q_text, intent, target in tamil_queries:
        for _ in range(40):
            samples.append({
                "text": q_text,
                "language": "tamil",
                "category": "tamil_nl_query",
                "is_synthetic": True,
                "ground_truth": {
                    "actor": "Unspecified",
                    "amount": 0,
                    "direction": "query",
                    "event_type": intent,
                    "target": target
                }
            })

    random.shuffle(samples)
    return samples


def generate_hindi_corpus() -> list:
    """Generates >2,000 realistic, domain-accurate financial bookkeeping sentences in Hindi."""
    samples = []
    
    # 1. Spoken Hindi Numerals & Hinglish (e.g. 'Rahul paanch sau dena hai agle hafte')
    for _ in range(600):
        actor = random.choice(HINDI_ACTORS) + random.choice(HINDI_HONORIFICS)
        amount_num, amount_spoken = random.choice(HINDI_SPOKEN_NUMS)
        temp_phrase, role, offset = random.choice(HINDI_TEMPORAL_PHRASES)
        
        templates = [
            (f"{actor} se {amount_spoken} lena hai {temp_phrase}", "receivable", "payment_commitment" if role == "DUE_DATE" else "receivable_obligation"),
            (f"{actor} ne {temp_phrase} {amount_spoken} diya", "receivable", "partial_payment"),
            (f"Supplier ko {amount_spoken} dena hai {temp_phrase}", "payable", "payable_obligation"),
            (f"{actor} se {amount_spoken} aana hai", "receivable", "receivable_invoice"),
            (f"{actor} {temp_phrase} ko {amount_spoken} dega bola", "receivable", "payment_commitment"),
            (f"{actor} ko {amount_spoken} advance bhej diya", "payable", "advance_payment")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language": "hindi",
            "category": "spoken_hindi_numerals",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor.strip(),
                "amount": amount_num,
                "direction": direction,
                "event_type": event_type,
                "temporal_role": role
            }
        })

    # 2. Pure Devanagari Hindi Script Category (e.g. 'राहुल से ₹2500 बाकी है')
    for _ in range(600):
        actor = random.choice(HINDI_SCRIPT_ACTORS)
        amount = random.choice([500, 1000, 1500, 2000, 2500, 3000, 5000, 8000, 10000, 25000])
        templates = [
            (f"{actor} से {amount} बाकी है", "receivable", "receivable_invoice"),
            (f"{actor} ने कल {amount} जमा किया", "receivable", "partial_payment"),
            (f"सप्लायर को {amount} देना है", "payable", "payable_obligation"),
            (f"{actor} ने शुक्रवार को {amount} देने को बोला", "receivable", "payment_commitment"),
            (f"{actor} को {amount} एडवांस भेज दिया", "payable", "advance_payment"),
            (f"{actor} को {amount} का माल उधार पे दिया", "receivable", "credit_sale"),
            (f"{actor} ने पूरा हिसाब चुकता कर दिया", "receivable", "full_settlement", 0)
        ]
        chosen = random.choice(templates)
        text = chosen[0]
        direction = chosen[1]
        event_type = chosen[2]
        amt_val = chosen[3] if len(chosen) > 3 else amount
        
        samples.append({
            "text": text,
            "language": "hindi",
            "category": "hindi_script",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor,
                "amount": amt_val,
                "direction": direction,
                "event_type": event_type
            }
        })

    # 3. Hinglish / Code-Mixed Hindi-English (e.g. 'Amit ko 2500 pending hai, GPay kiya')
    for _ in range(500):
        actor = random.choice(HINDI_ACTORS) + random.choice(HINDI_HONORIFICS)
        amount = random.choice([750, 1200, 2000, 2500, 3500, 4800, 5000, 8000, 12000, 25000])
        method = random.choice(["cash", "online", "gpay", "phonepe", "bank transfer"])
        
        templates = [
            (f"{actor} se {amount} pending hai", "receivable", "receivable_invoice"),
            (f"{actor} ne kal {amount} {method} se diya", "receivable", "partial_payment"),
            (f"Supplier ko {amount} pay karna hai", "payable", "payable_obligation"),
            (f"{actor} se {amount} milna hai", "receivable", "receivable_invoice"),
            (f"{actor} Friday ko {amount} de dunga bola", "receivable", "payment_commitment"),
            (f"{actor} ne sab clear kar diya", "receivable", "full_settlement", 0)
        ]
        chosen = random.choice(templates)
        text = chosen[0]
        direction = chosen[1]
        event_type = chosen[2]
        amt_val = chosen[3] if len(chosen) > 3 else amount
        
        samples.append({
            "text": text,
            "language": "hindi",
            "category": "code_mixed_hinglish",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor.strip(),
                "amount": amt_val,
                "direction": direction,
                "event_type": event_type
            }
        })

    # 4. Hindi Analytical Financial Queries (e.g. 'किसको कितना देना है', 'sabse zyada kisse lena hai')
    hindi_queries = [
        ("sabse zyada kisse lena hai", "TOP_DEBTORS", "customers"),
        ("सबसे ज्यादा किससे लेना है", "TOP_DEBTORS", "customers"),
        ("suppliers ko kitna dena hai", "TOTAL_PAYABLES", "suppliers"),
        ("सप्लायर्स को कितना देना है", "TOTAL_PAYABLES", "suppliers"),
        ("customers se kitna lena hai", "TOTAL_RECEIVABLES", "customers"),
        ("कस्टमर्स से कितना लेना है", "TOTAL_RECEIVABLES", "customers"),
        ("agle hafte ke payments", "UPCOMING_PAYMENTS", "payment_commitments"),
        ("kal ke payments", "UPCOMING_PAYMENTS", "payment_commitments"),
        ("overdue payments kiske hain", "OVERDUE_CUSTOMERS", "customers")
    ]
    for q_text, intent, target in hindi_queries:
        for _ in range(40):
            samples.append({
                "text": q_text,
                "language": "hindi",
                "category": "hindi_nl_query",
                "is_synthetic": True,
                "ground_truth": {
                    "actor": "Unspecified",
                    "amount": 0,
                    "direction": "query",
                    "event_type": intent,
                    "target": target
                }
            })

    random.shuffle(samples)
    return samples


def generate_telugu_sample_pool() -> list:
    """Generates standard Telugu sample pool."""
    samples = []
    
    # 1. Spoken Telugu Numerals
    for _ in range(700):
        actor = random.choice(TELUGU_ACTORS) + random.choice(TELUGU_HONORIFICS)
        amount_num, amount_spoken = random.choice(TELUGU_SPOKEN_NUMS)
        temp_phrase = random.choice(["ninna", "repu", "ee roju", "vache vaaram", "Friday ki"])
        role = "DUE_DATE" if temp_phrase in ["repu", "vache vaaram", "Friday ki"] else "EVENT_DATE"
        
        templates = [
            (f"{actor} {amount_spoken} ivvali {temp_phrase}", "receivable", "payment_commitment" if role == "DUE_DATE" else "receivable_obligation"),
            (f"{actor} {temp_phrase} {amount_spoken} ichadu", "receivable", "partial_payment"),
            (f"Supplier ki {amount_spoken} ivvali {temp_phrase}", "payable", "payable_obligation"),
            (f"{actor} nundi {amount_spoken} ravali", "receivable", "receivable_invoice"),
            (f"{actor} {temp_phrase} ki {amount_spoken} istanu annadu", "receivable", "payment_commitment")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language": "telugu",
            "language_category": "spoken_telugu_numerals",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor.strip(),
                "amount": amount_num,
                "direction": direction,
                "event_type": event_type,
                "temporal_role": role
            }
        })
        
    # 2. Telugu Script
    for _ in range(600):
        actor = random.choice(TELUGU_SCRIPT_ACTORS)
        amount = random.choice([500, 1000, 1500, 2000, 2500, 3000, 5000, 8000, 10000])
        templates = [
            (f"{actor} కి {amount} పెండింగ్ ఉంది", "receivable", "receivable_invoice"),
            (f"{actor} నిన్న {amount} ఇచ్చాడు", "receivable", "partial_payment"),
            (f"సప్లయర్ కి {amount} ఇవ్వాలి", "payable", "payable_obligation"),
            (f"{actor} శుక్రవారం కి {amount} ఇస్తాను అన్నాడు", "receivable", "payment_commitment"),
            (f"{actor} కి {amount} అడ్వాన్స్ పంపాము", "payable", "advance_payment")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language": "telugu",
            "language_category": "telugu_script",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor,
                "amount": amount,
                "direction": direction,
                "event_type": event_type
            }
        })

    # 3. Romanized Telugu & Code-Mixed
    for _ in range(800):
        actor = random.choice(TELUGU_ACTORS) + random.choice(TELUGU_HONORIFICS)
        amount = random.choice([750, 1200, 2000, 2500, 3500, 4800, 5000, 8000, 12000, 25000])
        method = random.choice(["cash", "online", "gpay", "phonepe", "bank transfer"])
        
        templates = [
            (f"{actor} ki {amount} pending undi", "receivable", "receivable_invoice"),
            (f"{actor} ninna {amount} {method} dwara ichadu", "receivable", "partial_payment"),
            (f"Supplier ki {amount} ivvali", "payable", "payable_obligation"),
            (f"{actor} nundi {amount} ravali", "receivable", "receivable_invoice"),
            (f"{actor} Friday ki remaining {amount} istanu annadu", "receivable", "payment_commitment"),
            (f"{actor} ki {amount} goods ichamu credit meeda", "receivable", "credit_sale")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language": "telugu",
            "language_category": "code_mixed_clean",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor.strip(),
                "amount": amount,
                "direction": direction,
                "event_type": event_type
            }
        })
        
    return samples


def main():
    print("=" * 60)
    print("Generating Full Multi-Lingual Financial Datasets & Corpuses...")
    print("=" * 60)
    
    # 1. Generate Dedicated Tamil Corpus
    tamil_corpus = generate_tamil_corpus()
    tamil_path = DATASET_DIR / "tamil_financial_corpus.json"
    with open(tamil_path, "w", encoding="utf-8") as f:
        json.dump(tamil_corpus, f, indent=2, ensure_ascii=False)
    print(f"-> Saved Tamil Corpus ({len(tamil_corpus)} samples) to: {tamil_path}")
    
    # 2. Generate Dedicated Hindi Corpus
    hindi_corpus = generate_hindi_corpus()
    hindi_path = DATASET_DIR / "hindi_financial_corpus.json"
    with open(hindi_path, "w", encoding="utf-8") as f:
        json.dump(hindi_corpus, f, indent=2, ensure_ascii=False)
    print(f"-> Saved Hindi Corpus ({len(hindi_corpus)} samples) to: {hindi_path}")

    # 3. Generate Combined Synthetic Corpus
    telugu_corpus = generate_telugu_sample_pool()
    combined_corpus = telugu_corpus + tamil_corpus + hindi_corpus
    random.shuffle(combined_corpus)
    combined_path = DATASET_DIR / "synthetic_financial_corpus.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined_corpus, f, indent=2, ensure_ascii=False)
    print(f"-> Saved Unified Multi-Lingual Corpus ({len(combined_corpus)} samples) to: {combined_path}")

    # 4. Generate Multi-Lingual Gold Benchmark Testset
    gold_benchmark = (
        telugu_corpus[:150] +
        [s for s in tamil_corpus if s["category"] != "tamil_nl_query"][:150] +
        [s for s in hindi_corpus if s["category"] != "hindi_nl_query"][:150]
    )
    for item in gold_benchmark:
        if "language_category" not in item:
            item["language_category"] = item.get("category", "code_mixed_indic")
            
    random.shuffle(gold_benchmark)
    gold_path = DATASET_DIR / "gold_benchmark_testset.json"
    with open(gold_path, "w", encoding="utf-8") as f:
        json.dump(gold_benchmark, f, indent=2, ensure_ascii=False)
    print(f"-> Saved Multi-Lingual Gold Benchmark ({len(gold_benchmark)} samples) to: {gold_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
