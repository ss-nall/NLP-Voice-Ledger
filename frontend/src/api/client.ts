/**
 * REST API Client for Bilingual Financial Event Intelligence Platform.
 */

const API_BASE = "http://localhost:8000/api";

export interface SpokenTextResponse {
  message_type: string;
  success?: boolean;
  requires_confirmation?: boolean;
  confirmation_prompt?: string;
  severity?: string;
  text_response: string;
  ledger_update?: any;
  nlp_diagnostics?: any;
  speech_data?: {
    raw_spoken_transcript: string;
    normalized_transcript: string;
    spoken_amounts: any[];
    audio_confidence: number;
    waveform_data: number[];
    tts_response: {
      telugu: string;
      english: string;
    };
  };
  rag_sources?: any[];
  data?: any;
}

export const api = {
  // Voice & Speech
  processSpokenText: async (transcript: string, sessionId = "voice_session", confidence = 0.95): Promise<SpokenTextResponse> => {
    const res = await fetch(`${API_BASE}/voice/process-spoken-text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript, session_id: sessionId, confidence })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  getSamplePrompts: async () => {
    const res = await fetch(`${API_BASE}/voice/sample-prompts`);
    return res.json();
  },

  // Conversation
  sendMessage: async (message: string, sessionId = "default_session", isVoice = false): Promise<SpokenTextResponse> => {
    const res = await fetch(`${API_BASE}/conversation/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId, is_voice: isVoice })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  confirmEvent: async (
    eventDict: any,
    overrideAmount?: number,
    forceSettle = false,
    sessionId = "default_session",
    selectedEntityId?: number,
    overrideActor?: string,
    linkAsAlias = true
  ) => {
    const res = await fetch(`${API_BASE}/conversation/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event_dict: eventDict,
        override_amount: overrideAmount,
        force_settle: forceSettle,
        session_id: sessionId,
        selected_entity_id: selectedEntityId,
        override_actor: overrideActor,
        link_as_alias: linkAsAlias
      })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  getConversationHistory: async (sessionId = "default_session") => {
    const res = await fetch(`${API_BASE}/conversation/history?session_id=${sessionId}`);
    return res.json();
  },

  resetSession: async (sessionId = "default_session") => {
    const res = await fetch(`${API_BASE}/conversation/reset-session?session_id=${sessionId}`, { method: "POST" });
    return res.json();
  },

  // Ledger & Transactions
  getTransactions: async (params?: { direction?: string; counterparty_type?: string; transaction_type?: string; status?: string; search?: string; limit?: number | string }) => {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`${API_BASE}/ledger/transactions?${query}`);
    return res.json();
  },

  getEvents: async () => {
    const res = await fetch(`${API_BASE}/ledger/events`);
    return res.json();
  },

  getCommitments: async (status?: string) => {
    const query = status ? `?status=${status}` : "";
    const res = await fetch(`${API_BASE}/ledger/commitments${query}`);
    return res.json();
  },

  getAuditLogs: async () => {
    const res = await fetch(`${API_BASE}/ledger/audit-logs`);
    return res.json();
  },

  updateTransaction: async (txId: string, data: {
    amount?: number;
    counterparty_name?: string;
    direction?: string;
    transaction_type?: string;
    payment_method?: string;
    date?: string;
  }) => {
    const res = await fetch(`${API_BASE}/ledger/transactions/${txId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  deleteTransaction: async (txId: string) => {
    const res = await fetch(`${API_BASE}/ledger/transactions/${txId}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  correctTransaction: async (txId: string, correctedAmount?: number, reason = "User edit") => {
    const res = await fetch(`${API_BASE}/ledger/correct-transaction`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transaction_id: txId, corrected_amount: correctedAmount, reason })
    });
    return res.json();
  },

  resetAllLedger: async () => {
    const res = await fetch(`${API_BASE}/ledger/reset-all`, { method: "POST" });
    return res.json();
  },

  seedDemoData: async () => {
    const res = await fetch(`${API_BASE}/ledger/seed-demo`, { method: "POST" });
    return res.json();
  },

  // Entities & Business
  getBusiness: async () => {
    const res = await fetch(`${API_BASE}/entities/business`);
    return res.json();
  },

  updateBusiness: async (name: string, ownerName = "", phone = "") => {
    const res = await fetch(`${API_BASE}/entities/business`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, owner_name: ownerName, phone })
    });
    return res.json();
  },

  getCustomers: async () => {
    const res = await fetch(`${API_BASE}/entities/customers`);
    return res.json();
  },

  getCustomerDetails: async (id: number) => {
    const res = await fetch(`${API_BASE}/entities/customers/${id}`);
    return res.json();
  },

  getSuppliers: async () => {
    const res = await fetch(`${API_BASE}/entities/suppliers`);
    return res.json();
  },

  getSupplierDetails: async (id: number) => {
    const res = await fetch(`${API_BASE}/entities/suppliers/${id}`);
    return res.json();
  },

  // Analytics
  getOverview: async () => {
    const res = await fetch(`${API_BASE}/analytics/overview`);
    return res.json();
  },

  getAging: async () => {
    const res = await fetch(`${API_BASE}/analytics/aging`);
    return res.json();
  },

  getCashflow: async (days = 30) => {
    const res = await fetch(`${API_BASE}/analytics/cashflow?days=${days}`);
    return res.json();
  },

  getTopDebtors: async (limit = 5) => {
    const res = await fetch(`${API_BASE}/analytics/top-debtors?limit=${limit}`);
    return res.json();
  },

  // Reminders & Health
  getReminders: async () => {
    const res = await fetch(`${API_BASE}/analytics/reminders`);
    return res.json();
  },

  getHealth: async () => {
    const res = await fetch(`${API_BASE}/ledger/health`);
    return res.json();
  },

  getJournal: async (limit = 50) => {
    const res = await fetch(`${API_BASE}/ledger/journal?limit=${limit}`);
    return res.json();
  },

  // Reminders
  generateReminder: async (customerName: string, amount: number, dueDate: string, phone = "") => {
    const res = await fetch(`${API_BASE}/reminders/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer_name: customerName, amount, due_date: dueDate, phone })
    });
    return res.json();
  },

  // RAG & Documents
  getDocuments: async () => {
    const res = await fetch(`${API_BASE}/documents`);
    return res.json();
  },

  queryRAG: async (question: string) => {
    const res = await fetch(`${API_BASE}/documents/rag-query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    return res.json();
  },

  // Benchmark Experiment
  runExperiment: async () => {
    const res = await fetch(`${API_BASE}/benchmark/run-experiment`);
    return res.json();
  }
};
