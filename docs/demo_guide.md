# 5-10 Minute Technical Demo & Interview Walkthrough Guide

Use this guide to demonstrate the platform effectively during technical reviews and evaluations.

---

## Step 1: Start the Servers

In Terminal 1 (Backend):
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

In Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173).

---

## Step 2: Live Demonstration Sequence

### Turn 1: Voice Recognition MVP & Spoken Numerals
1. Navigate to **Voice & Chat**.
2. Click the 1-click prompt or speak into the microphone:
   > *"Ramesh Aidhu vandalu ivvali vache vaaram"*
3. **What to highlight**:
   - The Speech Recognition engine decoded *"aidhu vandalu"* into **₹500** without digits.
   - The temporal phrase *"vache vaaram"* calculated the exact due date for next week.
   - The step-by-step **Pipeline Inspector** displays each stage's trace.
   - Ramesh's balance is updated to **₹500** with state `PAYMENT_PROMISED`.

---

### Turn 2: Multi-Turn Coreference Resolution
1. Type or speak:
   > *"Ninna 200 ichadu"*
2. **What to highlight**:
   - The user omitted the subject ("who?"). The system looked backwards through conversational memory and resolved Actor = **Ramesh**.
   - *"Ninna"* set event date to yesterday.
   - Partial payment of ₹200 applied, reducing Ramesh's balance to **₹300** with state `PARTIAL_PAYMENT`.

---

### Turn 3: Directional Semantics (*ki ivvali* vs *nundi ravali*)
1. Speak or type:
   > *"Supplier ki 8000 ivvali"*
2. **What to highlight**:
   - The system understands that *"ki ivvali"* represents a **Payable obligation** (money we owe) rather than a receivable asset.
   - The ₹8,000 is routed to **Supplier Payables** sub-ledger.

---

### Turn 4: Deterministic Natural Language Financial Query
1. Ask the system:
   > *"Evaru naaku ekkuva money ivvali?"*
2. **What to highlight**:
   - The LLM did **not** perform arithmetic itself.
   - The NL Query Parser mapped the intent to `TOP_DEBTORS`, queried the SQL database deterministically, and returned the ranked list with zero calculation error.

---

### Turn 5: Contradiction & Overpayment Interceptor
1. Speak or type:
   > *"Ramesh complete ga payment ichesadu"*
2. **What to highlight**:
   - The ledger knows Ramesh still has ₹300 pending.
   - Instead of blindly overwriting the record, the **Consistency Engine** intercepts the contradiction and displays an interactive confirmation modal with live balance comparison!

---

### Turn 6: Bilingual WhatsApp Payment Reminders
1. Navigate to **Receivables**.
2. Click **Send Reminder** for Ramesh.
3. **What to highlight**:
   - View auto-generated personalized reminder messages in **Telugu Script**, **Romanized Telugu**, and **English**.
   - Click **Open in WhatsApp** to launch the direct chat link.

---

### Turn 7: Scientific Research Benchmark Lab
1. Navigate to **Research Benchmark**.
2. **What to highlight**:
   - View empirical evaluation across **Approach A (Direct LLM)**, **Approach B (NLP+LLM)**, and **Approach C (Explicit NLP + State Machine)**.
   - Show how Approach C achieves **0% arithmetic hallucination** and **1.5ms latency** compared to Approach A's 37.5% failure rate.
