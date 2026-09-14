import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Mic,
  MicOff,
  Volume2,
  Trash2,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Bot,
  User,
  CheckCircle,
  FileText,
  Layers,
  ArrowUpRight,
  ArrowDownLeft,
  Calendar,
  Clock,
  RotateCcw,
  PlusCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  History,
  MessageSquare,
  X,
  Plus,
  Edit3,
  CheckCircle2,
  UserPlus
} from 'lucide-react';
import { api, SpokenTextResponse } from '../api/client';
import { PipelineVisualizer } from '../components/PipelineVisualizer';
import { ContradictionModal } from '../components/ContradictionModal';
import { DisambiguationModal } from '../components/DisambiguationModal';
import { DiscrepancyCard } from '../components/DiscrepancyCard';
import { DisambiguationCard } from '../components/DisambiguationCard';
import { EditTransactionModal } from '../components/EditTransactionModal';
import { notifyLedgerUpdated } from '../utils/events';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'system';
  text: string;
  isVoice?: boolean;
  isWelcome?: boolean;
  isError?: boolean;
  messageType?: string;
  ledgerUpdate?: any;
  nlpDiagnostics?: any;
  ragSources?: any[];
  time: string;
  disambiguationData?: any;
  contradictionData?: any;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
}

const STORAGE_SESSIONS_KEY = 'nlpledger_chat_sessions_v1';
const STORAGE_ACTIVE_ID_KEY = 'nlpledger_active_session_id_v1';

const createWelcomeMessage = (): ChatMessage => ({
  id: `welcome_${Date.now()}`,
  sender: 'system',
  text: '🙏 **నమస్కారం! మీ డిజిటల్ లెక్కల పుస్తకం సిద్ధంగా ఉంది.**\n*(Namaskaram! Welcome to your Voice FinTech Ledger Assistant)*\n\nమీరు తెలుగు లేదా ఇంగ్లీష్ లో మాట్లాడవచ్చు లేదా టైప్ చేయవచ్చు.\n*(Speak or type freely in Romanized Telugu, Telugu script, or English.)*',
  isWelcome: true,
  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
});

const createInitialSession = (): ChatSession => {
  const newId = `session_${Date.now()}`;
  return {
    id: newId,
    title: 'కొత్త సంభాషణ (New Chat)',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    messages: [createWelcomeMessage()]
  };
};

export const ConversationView: React.FC = () => {
  // Session & Message State
  const [sessions, setSessions] = useState<ChatSession[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_SESSIONS_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {
      console.error("Error reading saved chat sessions:", e);
    }
    const initial = createInitialSession();
    return [initial];
  });

  const [activeSessionId, setActiveSessionId] = useState<string>(() => {
    try {
      const savedId = localStorage.getItem(STORAGE_ACTIVE_ID_KEY);
      if (savedId) return savedId;
    } catch (e) {
      console.error("Error reading active session ID:", e);
    }
    return '';
  });

  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [latestDiagnostics, setLatestDiagnostics] = useState<any>(null);
  const [showInspector, setShowInspector] = useState(false);
  const [showHistoryDrawer, setShowHistoryDrawer] = useState(false);

  // Voice Recording State
  const [isRecording, setIsRecording] = useState(false);
  const [liveVoiceTranscript, setLiveVoiceTranscript] = useState('');
  const [speechLang, setSpeechLang] = useState<'te-IN' | 'en-IN'>('te-IN');
  const recognitionRef = useRef<any>(null);
  const transcriptRef = useRef<string>('');
  const hasSubmittedThisTurnRef = useRef<boolean>(false);
  const isSendingRef = useRef<boolean>(false);
  const lastSentRef = useRef<{ text: string; time: number }>({ text: '', time: 0 });

  // Contradiction Modal State
  const [contradictionData, setContradictionData] = useState<any>(null);
  const [isContradictionModalOpen, setIsContradictionModalOpen] = useState(false);

  // Disambiguation Modal State
  const [disambiguationData, setDisambiguationData] = useState<any>(null);
  const [isDisambiguationModalOpen, setIsDisambiguationModalOpen] = useState(false);

  // Edit & Delete Transaction Modal State
  const [selectedTxForEdit, setSelectedTxForEdit] = useState<any>(null);
  const [isEditTxModalOpen, setIsEditTxModalOpen] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Ensure valid activeSessionId
  useEffect(() => {
    if (!activeSessionId || !sessions.some(s => s.id === activeSessionId)) {
      if (sessions.length > 0) {
        setActiveSessionId(sessions[0].id);
      } else {
        const fresh = createInitialSession();
        setSessions([fresh]);
        setActiveSessionId(fresh.id);
      }
    }
  }, [sessions, activeSessionId]);

  // Persist sessions and activeSessionId to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_SESSIONS_KEY, JSON.stringify(sessions));
      if (activeSessionId) {
        localStorage.setItem(STORAGE_ACTIVE_ID_KEY, activeSessionId);
      }
    } catch (e) {
      console.error("Error saving chat sessions to localStorage:", e);
    }
  }, [sessions, activeSessionId]);

  const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];
  const messages = activeSession ? activeSession.messages : [];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, liveVoiceTranscript, isRecording, isProcessing]);

  // Start a New Chat
  const handleStartNewChat = () => {
    const newSession = createInitialSession();
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    setInputText('');
    setLiveVoiceTranscript('');
    transcriptRef.current = '';
    setLatestDiagnostics(null);
    setShowInspector(false);
    setShowHistoryDrawer(false);

    // Also reset backend multi-turn tracker for this new session
    api.resetSession(newSession.id).catch(err => console.warn(err));
  };

  // Switch to a previous session
  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
    setShowHistoryDrawer(false);
    const target = sessions.find(s => s.id === sessionId);
    if (target && target.messages.length > 0) {
      const lastBot = [...target.messages].reverse().find(m => m.nlpDiagnostics);
      setLatestDiagnostics(lastBot ? lastBot.nlpDiagnostics : null);
    } else {
      setLatestDiagnostics(null);
    }
  };

  // Delete a session
  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const remaining = sessions.filter(s => s.id !== sessionId);
    if (remaining.length === 0) {
      const fresh = createInitialSession();
      setSessions([fresh]);
      setActiveSessionId(fresh.id);
    } else {
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        setActiveSessionId(remaining[0].id);
      }
    }
  };

  // Clear current active chat messages
  const handleClearCurrentChat = () => {
    if (!activeSession) return;
    const resetWelcome = createWelcomeMessage();
    setSessions(prev =>
      prev.map(s =>
        s.id === activeSessionId
          ? { ...s, title: 'కొత్త సంభాషణ (New Chat)', messages: [resetWelcome], updatedAt: new Date().toISOString() }
          : s
      )
    );
    setLatestDiagnostics(null);
    api.resetSession(activeSessionId).catch(err => console.warn(err));
  };

  // Clear all data and reset fresh
  const handleClearAllData = async () => {
    if (window.confirm("Are you sure you want to clear all ledger data and start completely fresh from scratch?")) {
      try {
        setIsProcessing(true);
        await api.resetAllLedger();
        const fresh = createInitialSession();
        setSessions([fresh]);
        setActiveSessionId(fresh.id);
        setLatestDiagnostics(null);
      } catch (err: any) {
        alert("Failed to reset ledger: " + err.message);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  // Web Speech API Voice Handler with Live Transcript Accumulation
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Browser speech recognition is not supported in this browser. Please type in the text box below.");
      return;
    }

    try {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }

      transcriptRef.current = '';
      hasSubmittedThisTurnRef.current = false;
      setLiveVoiceTranscript('');
      setIsRecording(true);

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = speechLang;

      recognition.onstart = () => {
        setIsRecording(true);
      };

      recognition.onresult = (event: any) => {
        let interim = '';
        let final = '';
        for (let i = 0; i < event.results.length; ++i) {
          const res = event.results[i];
          if (res.isFinal) {
            final += res[0].transcript + ' ';
          } else {
            interim += res[0].transcript;
          }
        }
        const accumulated = (final + interim).trim();
        if (accumulated) {
          transcriptRef.current = accumulated;
          setLiveVoiceTranscript(accumulated);
        }
      };

      recognition.onend = () => {
        setIsRecording(false);
        const finalSpoken = transcriptRef.current.trim();
        if (finalSpoken && !hasSubmittedThisTurnRef.current) {
          hasSubmittedThisTurnRef.current = true;
          handleSendMessage(finalSpoken, true);
          transcriptRef.current = '';
          setLiveVoiceTranscript('');
        }
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition event notice:", event.error);
        if (event.error !== 'no-speech') {
          setIsRecording(false);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e) {
      console.error("Speech recognition startup error:", e);
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        console.warn("Speech recognition stop error:", e);
      }
    }
    const finalSpoken = transcriptRef.current.trim();
    if (finalSpoken && !hasSubmittedThisTurnRef.current) {
      hasSubmittedThisTurnRef.current = true;
      handleSendMessage(finalSpoken, true);
      transcriptRef.current = '';
      setLiveVoiceTranscript('');
    }
  };

  const handleSendMessage = async (textToSend: string, isVoice = false) => {
    const trimmed = textToSend.trim();
    const now = Date.now();

    // Prevent concurrent, empty, or duplicate rapid submissions
    if (!trimmed || isProcessing || isSendingRef.current) return;
    if (lastSentRef.current.text === trimmed.toLowerCase() && (now - lastSentRef.current.time) < 1500) {
      console.warn("Deduplicated rapid duplicate send:", trimmed);
      return;
    }

    isSendingRef.current = true;
    lastSentRef.current = { text: trimmed.toLowerCase(), time: now };
    hasSubmittedThisTurnRef.current = true;

    const targetSessionId = activeSessionId || (sessions[0] ? sessions[0].id : `session_${Date.now()}`);

    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: trimmed,
      isVoice,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    // Immediately insert User Message directly into chat UI
    setSessions(prev =>
      prev.map(s => {
        if (s.id === targetSessionId) {
          const isDefaultTitle = s.title.includes('కొత్త సంభాషణ') || s.title.includes('New Chat');
          const newTitle = isDefaultTitle
            ? (trimmed.length > 28 ? trimmed.slice(0, 28) + '...' : trimmed)
            : s.title;
          return {
            ...s,
            title: newTitle,
            updatedAt: new Date().toISOString(),
            messages: [...s.messages, userMsg]
          };
        }
        return s;
      })
    );

    setInputText('');
    setLiveVoiceTranscript('');
    transcriptRef.current = '';
    setIsProcessing(true);

    try {
      const response: SpokenTextResponse = isVoice
        ? await api.processSpokenText(trimmed, targetSessionId)
        : await api.sendMessage(trimmed, targetSessionId);

      handleProcessResponse(response, targetSessionId);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `sys_err_${Date.now()}`,
        sender: 'system',
        text: `⚠️ **Error Processing**: ${err.message}`,
        isError: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setSessions(prev =>
        prev.map(s =>
          s.id === targetSessionId
            ? { ...s, messages: [...s.messages, errorMsg] }
            : s
        )
      );
    } finally {
      setIsProcessing(false);
      isSendingRef.current = false;
    }
  };

  const handleProcessResponse = (response: SpokenTextResponse, targetSessionId?: string) => {
    const sessId = targetSessionId || activeSessionId;
    setLatestDiagnostics(response.nlp_diagnostics);

    if (response.message_type === 'ENTITY_DISAMBIGUATION_REQUIRED' || (response as any).requires_disambiguation) {
      setDisambiguationData(response);
    } else if (response.requires_confirmation || response.message_type === 'CONTRADICTION_CONFIRMATION_REQUIRED') {
      setContradictionData(response);
    }

    if (response.ledger_update) {
      notifyLedgerUpdated();
    }

    const botMsg: ChatMessage = {
      id: `bot_${Date.now()}`,
      sender: 'system',
      text: response.text_response,
      messageType: response.message_type,
      ledgerUpdate: response.ledger_update,
      nlpDiagnostics: response.nlp_diagnostics,
      ragSources: response.rag_sources,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      disambiguationData: (response.message_type === 'ENTITY_DISAMBIGUATION_REQUIRED' || (response as any).requires_disambiguation) ? response : undefined,
      contradictionData: (response.requires_confirmation || response.message_type === 'CONTRADICTION_CONFIRMATION_REQUIRED') ? response : undefined
    };

    setSessions(prev =>
      prev.map(s =>
        s.id === sessId
          ? { ...s, updatedAt: new Date().toISOString(), messages: [...s.messages, botMsg] }
          : s
      )
    );
  };

  const handleConfirmContradiction = async (overrideAmount?: number, forceSettle = false, customData?: any) => {
    const dataToUse = customData || contradictionData;
    if (!dataToUse?.proposed_event) return;

    try {
      setIsProcessing(true);
      const res = await api.confirmEvent(dataToUse.proposed_event, overrideAmount, forceSettle, activeSessionId);
      setIsContradictionModalOpen(false);
      setContradictionData(null);

      const confirmMsg: ChatMessage = {
        id: `bot_conf_${Date.now()}`,
        sender: 'system',
        text: res.text_response,
        ledgerUpdate: res.ledger_update,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setSessions(prev =>
        prev.map(s =>
          s.id === activeSessionId
            ? {
                ...s,
                updatedAt: new Date().toISOString(),
                messages: [
                  ...s.messages.map(m =>
                    m.contradictionData ? { ...m, contradictionData: { ...m.contradictionData, resolved: true, resolvedText: res.text_response } } : m
                  ),
                  confirmMsg
                ]
              }
            : s
        )
      );
      if (res.ledger_update) {
        notifyLedgerUpdated();
      }
    } catch (err: any) {
      alert("Error confirming event: " + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCancelContradiction = (customData?: any) => {
    setIsContradictionModalOpen(false);
    setContradictionData(null);
    const cancelMsg: ChatMessage = {
      id: `bot_cancel_${Date.now()}`,
      sender: 'system',
      text: '⚠️ **లావాదేవీ రద్దు చేయబడింది.** లెక్కల పుస్తకంలో ఎలాంటి మార్పు జరగలేదు.\n*(Transaction cancelled. No changes were made to the ledger.)*',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setSessions(prev =>
      prev.map(s =>
        s.id === activeSessionId
          ? {
              ...s,
              updatedAt: new Date().toISOString(),
              messages: [
                ...s.messages.map(m =>
                  m.contradictionData ? { ...m, contradictionData: { ...m.contradictionData, resolved: true, cancelled: true } } : m
                ),
                cancelMsg
              ]
            }
          : s
      )
    );
  };

  const handleSelectExistingEntity = async (entityId: number, entityName: string, customData?: any) => {
    const dataToUse = customData || disambiguationData;
    if (!dataToUse?.proposed_event) return;
    try {
      setIsProcessing(true);
      const res = await api.confirmEvent(
        dataToUse.proposed_event,
        undefined,
        false,
        activeSessionId,
        entityId,
        entityName,
        true
      );
      setIsDisambiguationModalOpen(false);
      setDisambiguationData(null);

      const confirmMsg: ChatMessage = {
        id: `bot_disamb_${Date.now()}`,
        sender: 'system',
        text: res.text_response,
        ledgerUpdate: res.ledger_update,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setSessions(prev =>
        prev.map(s =>
          s.id === activeSessionId
            ? {
                ...s,
                updatedAt: new Date().toISOString(),
                messages: [
                  ...s.messages.map(m =>
                    m.disambiguationData ? { ...m, disambiguationData: { ...m.disambiguationData, resolved: true, resolvedText: res.text_response } } : m
                  ),
                  confirmMsg
                ]
              }
            : s
        )
      );
      if (res.ledger_update) {
        notifyLedgerUpdated();
      }
    } catch (err: any) {
      alert("Error linking account: " + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCreateNewEntity = async (customData?: any) => {
    const dataToUse = customData || disambiguationData;
    if (!dataToUse?.proposed_event) return;
    try {
      setIsProcessing(true);
      const res = await api.confirmEvent(
        dataToUse.proposed_event,
        undefined,
        false,
        activeSessionId,
        undefined,
        dataToUse.extracted_actor,
        false
      );
      setIsDisambiguationModalOpen(false);
      setDisambiguationData(null);

      const confirmMsg: ChatMessage = {
        id: `bot_new_ent_${Date.now()}`,
        sender: 'system',
        text: res.text_response,
        ledgerUpdate: res.ledger_update,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setSessions(prev =>
        prev.map(s =>
          s.id === activeSessionId
            ? {
                ...s,
                updatedAt: new Date().toISOString(),
                messages: [
                  ...s.messages.map(m =>
                    m.disambiguationData ? { ...m, disambiguationData: { ...m.disambiguationData, resolved: true, resolvedText: res.text_response } } : m
                  ),
                  confirmMsg
                ]
              }
            : s
        )
      );
      if (res.ledger_update) {
        notifyLedgerUpdated();
      }
    } catch (err: any) {
      alert("Error creating new account: " + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCancelDisambiguation = (customData?: any) => {
    setIsDisambiguationModalOpen(false);
    setDisambiguationData(null);
    const cancelMsg: ChatMessage = {
      id: `bot_cancel_disamb_${Date.now()}`,
      sender: 'system',
      text: '⚠️ **ఖాతా ఎంపిక రద్దు చేయబడింది.** ఎలాంటి ఖాతా అనుసంధానం జరగలేదు.\n*(Account selection cancelled. No link was established.)*',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setSessions(prev =>
      prev.map(s =>
        s.id === activeSessionId
          ? {
              ...s,
              updatedAt: new Date().toISOString(),
              messages: [
                ...s.messages.map(m =>
                  m.disambiguationData ? { ...m, disambiguationData: { ...m.disambiguationData, resolved: true, cancelled: true } } : m
                ),
                cancelMsg
              ]
            }
          : s
      )
    );
  };

  const handleTransactionSavedInChat = (updatedTx: any) => {
    setSessions(prev =>
      prev.map(s =>
        s.id === activeSessionId
          ? {
              ...s,
              updatedAt: new Date().toISOString(),
              messages: s.messages.map(msg =>
                msg.ledgerUpdate && (msg.ledgerUpdate.transaction_id === updatedTx.transaction_id || msg.ledgerUpdate.id === updatedTx.transaction_id)
                  ? {
                      ...msg,
                      ledgerUpdate: {
                        ...msg.ledgerUpdate,
                        actor: updatedTx.counterparty_name,
                        amount: updatedTx.amount,
                        direction: updatedTx.direction,
                        current_balance: updatedTx.balance_after,
                        transaction_type: updatedTx.transaction_type,
                        is_edited: true
                      }
                    }
                  : msg
              )
            }
          : s
      )
    );
  };

  const handleTransactionDeletedInChat = (deletedId: string) => {
    setSessions(prev =>
      prev.map(s =>
        s.id === activeSessionId
          ? {
              ...s,
              updatedAt: new Date().toISOString(),
              messages: s.messages.map(msg =>
                msg.ledgerUpdate && (msg.ledgerUpdate.transaction_id === deletedId || msg.ledgerUpdate.id === deletedId)
                  ? {
                      ...msg,
                      ledgerUpdate: {
                        ...msg.ledgerUpdate,
                        is_deleted: true
                      }
                    }
                  : msg
              )
            }
          : s
      )
    );
  };

  const quickActions = [
    { label: '🔴 ఇవ్వాలి (To Pay)', prompt: 'Supplier ki 5000 ivvali next week', color: 'var(--payable-color)' },
    { label: '🟢 రావాలి (To Receive)', prompt: 'Customer nundi 3000 ravali', color: 'var(--receivable-color)' },
    { label: '💰 వచ్చింది (Received)', prompt: 'Customer 500 ichadu', color: 'var(--cyan)' },
    { label: '📊 లెక్కల సారాంశం (Summary)', prompt: 'Show my total payables and receivables summary', color: 'var(--amber)' },
    { label: '⏰ రాబోయే చెల్లింపులు (Due Dates)', prompt: 'Show upcoming payment commitments', color: '#818CF8' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 105px)', maxWidth: '1200px', margin: '0 auto', width: '100%', position: 'relative' }}>
      
      {/* Top Header & Session Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 18px', background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-color)', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'linear-gradient(135deg, #0284C7, #06B6D4)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', boxShadow: '0 4px 12px rgba(6, 182, 212, 0.3)' }}>
            <Bot size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                వాయిస్ ఖాతా అసిస్టెంట్ <span style={{ fontSize: '0.9rem', color: 'var(--cyan)', fontWeight: 500 }}>(Voice Khata)</span>
              </h2>
              <span className="badge badge-emerald" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                🟢 Live
              </span>
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              సహజంగా మాట్లాడండి: తెలుగు + English Code-Mixed Fintech Intelligence
            </div>
          </div>
        </div>

        {/* Action Controls & New Chat Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          
          {/* + NEW CHAT BUTTON */}
          <button
            onClick={handleStartNewChat}
            className="btn btn-primary"
            title="Start a new conversation session with fresh context"
          >
            <Plus size={16} />
            <span>+ New Chat / కొత్త సంభాషణ</span>
          </button>

          {/* CHAT HISTORY DRAWER TOGGLE */}
          <button
            onClick={() => setShowHistoryDrawer(!showHistoryDrawer)}
            className="btn btn-secondary"
            style={{
              borderColor: showHistoryDrawer ? 'var(--cyan)' : 'var(--border-color)',
              color: showHistoryDrawer ? 'var(--cyan)' : 'var(--text-main)'
            }}
            title="View past conversation sessions"
          >
            <History size={16} color={showHistoryDrawer ? 'var(--cyan)' : 'var(--text-dim)'} />
            <span>History ({sessions.length})</span>
          </button>

          {latestDiagnostics && (
            <button
              onClick={() => setShowInspector(!showInspector)}
              className="btn btn-secondary"
              style={{
                borderColor: showInspector ? 'var(--cyan)' : 'var(--border-color)',
                color: showInspector ? 'var(--cyan)' : 'var(--text-main)'
              }}
              title="Toggle Step-by-Step NLP Linguistic Trace"
            >
              <Layers size={16} color="var(--cyan)" />
              <span>{showInspector ? 'Hide Trace' : '🔍 NLP Trace'}</span>
            </button>
          )}

          {/* CLEAR CURRENT CHAT */}
          <button
            onClick={handleClearCurrentChat}
            className="btn btn-secondary"
            title="Clear messages in current chat session"
          >
            <Trash2 size={16} color="var(--text-dim)" />
            <span>Clear</span>
          </button>

          {/* RESET BOOK */}
          <button
            onClick={handleClearAllData}
            className="btn btn-danger-subtle"
            title="Wipe test data and start fresh with empty book"
          >
            <RotateCcw size={16} />
            <span>Reset Book</span>
          </button>
        </div>
      </div>

      {/* CHAT HISTORY DRAWER (Collapsible overlay) */}
      {showHistoryDrawer && (
        <div
          style={{
            position: 'absolute',
            top: '65px',
            right: '18px',
            width: '320px',
            maxHeight: '480px',
            background: 'var(--bg-card)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-color)',
            boxShadow: '0 12px 32px rgba(0,0,0,0.25)',
            zIndex: 100,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            animation: 'fadeIn 0.2s ease-in-out'
          }}
        >
          <div style={{ padding: '12px 16px', background: 'var(--bg-card-subtle)', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
              <History size={16} color="var(--cyan)" /> సంభాషణల చరిత్ర (Chat History)
            </div>
            <button
              onClick={() => setShowHistoryDrawer(false)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}
            >
              <X size={16} />
            </button>
          </div>

          <div style={{ overflowY: 'auto', padding: '8px', display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
            {sessions.map(s => {
              const isActive = s.id === activeSessionId;
              const dateStr = new Date(s.updatedAt || s.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
              return (
                <div
                  key={s.id}
                  onClick={() => handleSelectSession(s.id)}
                  style={{
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: isActive ? 'rgba(2, 132, 199, 0.12)' : 'transparent',
                    border: isActive ? '1px solid var(--accent-primary)' : '1px solid transparent',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseEnter={e => {
                    if (!isActive) e.currentTarget.style.background = 'var(--bg-card-subtle)';
                  }}
                  onMouseLeave={e => {
                    if (!isActive) e.currentTarget.style.background = 'transparent';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                    <MessageSquare size={15} color={isActive ? 'var(--cyan)' : 'var(--text-dim)'} style={{ flexShrink: 0 }} />
                    <div style={{ overflow: 'hidden' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: isActive ? 700 : 500, color: isActive ? 'var(--cyan)' : 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {s.title}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {s.messages.length} messages • {dateStr}
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={e => handleDeleteSession(s.id, e)}
                    style={{ background: 'transparent', border: 'none', color: 'var(--text-dim)', padding: '4px', cursor: 'pointer', borderRadius: '4px' }}
                    title="Delete this chat session"
                    onMouseEnter={e => (e.currentTarget.style.color = 'var(--payable-color)')}
                    onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-dim)')}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              );
            })}
          </div>

          <div style={{ padding: '10px 14px', borderTop: '1px solid var(--border-color)', background: 'var(--bg-card-subtle)' }}>
            <button
              onClick={handleStartNewChat}
              className="btn btn-primary"
              style={{ width: '100%', padding: '8px', fontSize: '0.82rem', fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
            >
              <Plus size={15} /> + Start New Chat
            </button>
          </div>
        </div>
      )}

      {/* Collapsible NLP Inspector Drawer */}
      {showInspector && latestDiagnostics && (
        <div style={{ marginBottom: '14px', animation: 'fadeIn 0.2s ease-in-out' }}>
          <PipelineVisualizer diagnostics={latestDiagnostics} />
        </div>
      )}



      {/* Main Spacious Chat Messages Stream */}
      <div
        className="fin-card"
        style={{
          flex: 1,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          padding: '24px',
          marginBottom: '14px',
          background: 'var(--bg-card)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-color)'
        }}
      >
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div
              key={m.id}
              style={{
                display: 'flex',
                gap: '12px',
                alignSelf: isUser ? 'flex-end' : 'flex-start',
                maxWidth: isUser ? '80%' : '85%',
                width: isUser ? 'auto' : '100%',
                animation: 'fadeIn 0.2s ease-in-out'
              }}
            >
              {!isUser && (
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg, #0284C7, #10B981)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', flexShrink: 0, marginTop: '2px' }}>
                  <Bot size={18} />
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start', width: '100%' }}>
                <div
                  style={{
                    background: isUser
                      ? m.isVoice
                        ? 'linear-gradient(135deg, #0284C7, #0891B2)'
                        : 'linear-gradient(135deg, #0284C7, #0369A1)'
                      : 'var(--chat-bot-bg)',
                    border: isUser
                      ? m.isVoice ? '1px solid rgba(6, 182, 212, 0.4)' : 'none'
                      : '1px solid var(--border-color)',
                    borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                    padding: '16px 20px',
                    color: isUser ? '#FFFFFF' : 'var(--chat-bot-text)',
                    fontSize: '0.96rem',
                    lineHeight: 1.6,
                    whiteSpace: 'pre-wrap',
                    boxShadow: isUser ? '0 4px 14px rgba(2, 132, 199, 0.3)' : '0 2px 8px rgba(0,0,0,0.06)',
                    maxWidth: isUser ? '100%' : '750px'
                  }}
                >
                  {/* Voice Prompt Badge Indicator */}
                  {isUser && m.isVoice && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                      <span style={{ fontSize: '0.72rem', background: 'rgba(0, 0, 0, 0.25)', color: '#FFFFFF', padding: '2px 8px', borderRadius: '12px', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '4px', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
                        <Mic size={12} /> 🎙️ Spoken Voice Prompt
                      </span>
                    </div>
                  )}

                  {m.text}

                  {/* Interactive Discrepancy Card */}
                  {m.contradictionData && (
                    <DiscrepancyCard
                      data={m.contradictionData}
                      onConfirm={(overrideAmount, forceSettle) =>
                        handleConfirmContradiction(overrideAmount, forceSettle, m.contradictionData)
                      }
                      onCancel={() => handleCancelContradiction(m.contradictionData)}
                      isProcessing={isProcessing}
                    />
                  )}

                  {/* Interactive Name Disambiguation Card */}
                  {m.disambiguationData && (
                    <DisambiguationCard
                      data={m.disambiguationData}
                      onSelectExisting={(id, name) =>
                        handleSelectExistingEntity(id, name, m.disambiguationData)
                      }
                      onCreateNew={() => handleCreateNewEntity(m.disambiguationData)}
                      onCancel={() => handleCancelDisambiguation(m.disambiguationData)}
                      isProcessing={isProcessing}
                    />
                  )}

                  {/* Financial Event Visual Badge Card */}
                  {m.ledgerUpdate && (
                    <div
                      style={{
                        marginTop: '12px',
                        padding: '14px 16px',
                        background: m.ledgerUpdate.is_deleted
                          ? 'rgba(239, 68, 68, 0.08)'
                          : m.ledgerUpdate.entity_type === 'supplier' ? 'var(--payable-light)' : 'var(--receivable-light)',
                        borderRadius: 'var(--radius-md)',
                        border: m.ledgerUpdate.is_deleted
                          ? '1px dashed #ef4444'
                          : m.ledgerUpdate.entity_type === 'supplier' ? '1px solid var(--payable-border)' : '1px solid var(--receivable-border)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px',
                        opacity: m.ledgerUpdate.is_deleted ? 0.75 : 1
                      }}
                    >
                      {m.ledgerUpdate.is_deleted ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#dc2626', fontSize: '0.85rem', fontWeight: 600 }}>
                          <Trash2 size={16} />
                          <span>ఈ లావాదేవీ తొలగించబడింది (Transaction Deleted & Balance Rolled Back)</span>
                        </div>
                      ) : (
                        <>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span
                                className={`badge ${m.ledgerUpdate.entity_type === 'supplier' ? 'badge-rose' : 'badge-emerald'}`}
                                style={{ fontSize: '0.75rem', fontWeight: 700, padding: '3px 8px' }}
                              >
                                {m.ledgerUpdate.entity_type === 'supplier' ? '🔴 ఇవ్వాలి (Payable to Supplier)' : '🟢 రావాలి (Receivable from Customer)'}
                              </span>
                              {m.ledgerUpdate.is_edited && (
                                <span className="badge badge-amber" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>
                                  ✏️ సవరించబడింది (Edited)
                                </span>
                              )}
                            </div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                              Tx #{m.ledgerUpdate.transaction_id || 'LOGGED'}
                            </span>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginTop: '4px' }}>
                            <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                              {m.ledgerUpdate.actor}
                            </span>
                            <span style={{ fontSize: '1.3rem', fontWeight: 800, color: m.ledgerUpdate.entity_type === 'supplier' ? 'var(--payable-color)' : 'var(--receivable-color)' }}>
                              ₹{Number(m.ledgerUpdate.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                            </span>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px dashed var(--border-color)', paddingTop: '6px', marginTop: '2px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            <span>మొత్తం బాకీ (Updated Balance):</span>
                            <strong style={{ color: 'var(--text-main)', fontSize: '0.9rem' }}>
                              ₹{Number(m.ledgerUpdate.current_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                            </strong>
                          </div>

                          {/* Inline Edit & Delete Actions */}
                          {m.ledgerUpdate.transaction_id && (
                            <div style={{ display: 'flex', gap: '8px', marginTop: '8px', borderTop: '1px solid var(--border-color)', paddingTop: '8px', justifyContent: 'flex-end' }}>
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedTxForEdit({
                                    id: m.ledgerUpdate.transaction_id,
                                    counterparty_name: m.ledgerUpdate.actor,
                                    amount: m.ledgerUpdate.amount,
                                    direction: m.ledgerUpdate.direction || (m.ledgerUpdate.entity_type === 'supplier' ? 'payable' : 'receivable'),
                                    transaction_type: m.ledgerUpdate.transaction_type || (m.ledgerUpdate.entity_type === 'supplier' ? 'PURCHASE' : 'CREDIT_SALE'),
                                    payment_method: m.ledgerUpdate.payment_method || 'cash',
                                    date: m.ledgerUpdate.date || new Date().toISOString().split('T')[0]
                                  });
                                  setIsEditTxModalOpen(true);
                                }}
                                className="btn btn-secondary"
                                style={{ padding: '4px 10px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
                              >
                                <Edit3 size={13} /> సవరించు (Edit)
                              </button>
                              <button
                                type="button"
                                onClick={async (e) => {
                                  e.stopPropagation();
                                  if (window.confirm("ఈ లావాదేవీని ఖచ్చితంగా తొలగించాలనుకుంటున్నారా? బాకీ నిల్వ ఆటోమేటిక్ గా రీసెట్ అవుతుంది.")) {
                                    try {
                                      await api.deleteTransaction(m.ledgerUpdate.transaction_id);
                                      handleTransactionDeletedInChat(m.ledgerUpdate.transaction_id);
                                    } catch (err: any) {
                                      alert("Error deleting transaction: " + err.message);
                                    }
                                  }
                                }}
                                className="btn btn-danger-subtle"
                                style={{ padding: '4px 10px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
                              >
                                <Trash2 size={13} /> తొలగించు (Delete)
                              </button>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px', padding: '0 4px' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    {m.isVoice ? '🎙 Voice Spoken • ' : ''}{m.time}
                  </span>
                </div>
              </div>

              {isUser && (
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: m.isVoice ? 'linear-gradient(135deg, #0284C7, #06B6D4)' : '#1E293B', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', flexShrink: 0, border: '1px solid var(--border-color)', marginTop: '2px' }}>
                  {m.isVoice ? <Mic size={18} /> : <User size={18} />}
                </div>
              )}
            </div>
          );
        })}

        {/* Live Audio Listening Card in Chat Stream */}
        {isRecording && (
          <div
            style={{
              display: 'flex',
              gap: '12px',
              alignSelf: 'flex-end',
              maxWidth: '85%',
              width: 'auto',
              animation: 'fadeIn 0.2s ease-in-out'
            }}
          >
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(2, 132, 199, 0.15), rgba(16, 185, 129, 0.12))',
                border: '1.5px solid var(--cyan)',
                borderRadius: '18px 18px 4px 18px',
                padding: '16px 20px',
                color: 'var(--text-main)',
                boxShadow: '0 0 25px rgba(6, 182, 212, 0.25)',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px',
                minWidth: '290px'
              }}
            >
              {/* Header with animated equalizer waveform */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--payable-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', animation: 'pulseGlow 1.2s infinite' }}>
                    <Mic size={16} />
                  </div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--cyan)' }}>
                    వింటున్నాము... (Listening Live)
                  </span>
                </div>

                {/* Animated Voice Waveform Bars */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '3px', height: '18px' }}>
                  <span style={{ width: '3px', height: '14px', background: '#06B6D4', borderRadius: '2px', animation: 'waveBar 0.8s infinite ease-in-out' }} />
                  <span style={{ width: '3px', height: '18px', background: '#10B981', borderRadius: '2px', animation: 'waveBar 0.6s infinite ease-in-out 0.15s' }} />
                  <span style={{ width: '3px', height: '10px', background: '#38BDF8', borderRadius: '2px', animation: 'waveBar 0.9s infinite ease-in-out 0.3s' }} />
                  <span style={{ width: '3px', height: '16px', background: '#F59E0B', borderRadius: '2px', animation: 'waveBar 0.7s infinite ease-in-out 0.2s' }} />
                </div>
              </div>

              {/* Real-time Transcribed Live Speech */}
              <div style={{ fontSize: '1.02rem', color: liveVoiceTranscript ? 'var(--text-main)' : 'var(--text-muted)', fontStyle: liveVoiceTranscript ? 'normal' : 'italic', fontWeight: liveVoiceTranscript ? 600 : 400, minHeight: '26px' }}>
                {liveVoiceTranscript ? `"${liveVoiceTranscript}"` : 'చెప్పండి... మీ మాటలు ఇక్కడ వెంటనే కనిపిస్తాయి (Speak now)...'}
              </div>

              {/* Action Button on Live Card */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px', borderTop: '1px solid var(--border-color)', paddingTop: '8px', marginTop: '2px' }}>
                <button
                  type="button"
                  onClick={stopRecording}
                  style={{
                    background: liveVoiceTranscript ? 'linear-gradient(135deg, #10B981, #059669)' : 'var(--payable-color)',
                    border: 'none',
                    borderRadius: '20px',
                    padding: '5px 14px',
                    color: '#fff',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                  }}
                >
                  <CheckCircle size={14} /> {liveVoiceTranscript ? 'పూర్తయింది (Send & Record)' : 'ఆపు (Stop)'}
                </button>
              </div>
            </div>

            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg, #0284C7, #06B6D4)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', flexShrink: 0, border: '1px solid var(--border-color)', marginTop: '2px' }}>
              <Mic size={18} />
            </div>
          </div>
        )}

        {/* Assistant Thinking / Processing State */}
        {isProcessing && !isRecording && (
          <div
            style={{
              display: 'flex',
              gap: '12px',
              alignSelf: 'flex-start',
              maxWidth: '85%',
              width: '100%',
              animation: 'fadeIn 0.2s ease-in-out'
            }}
          >
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg, #0284C7, #10B981)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', flexShrink: 0, marginTop: '2px' }}>
              <Bot size={18} />
            </div>
            <div
              style={{
                background: 'var(--chat-bot-bg)',
                border: '1px solid var(--border-color)',
                borderRadius: '18px 18px 18px 4px',
                padding: '14px 18px',
                color: 'var(--text-muted)',
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}
            >
              <div style={{ width: '16px', height: '16px', border: '2px solid var(--cyan)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
              <span>ద్విభాషా NLP ఆలోచిస్తోంది (Processing Telugu speech & financial ledger)...</span>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Quick Access Vernacular Suggestion Chips */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '10px', scrollbarWidth: 'none' }}>
        {/* Voice Test Demo Quick Chip */}
        <button
          onClick={() => handleSendMessage('రమేష్ కి 1000 కట్టాలి వచ్చే వారం', true)}
          disabled={isProcessing}
          style={{
            background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(2, 132, 199, 0.15))',
            border: '1px solid var(--cyan)',
            borderRadius: '20px',
            padding: '6px 14px',
            fontSize: '0.78rem',
            fontWeight: 700,
            color: 'var(--cyan)',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            transition: 'all 0.15s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
          title="Simulate Voice Prompt for Ramesh 1000 Payable"
        >
          <Mic size={13} color="var(--cyan)" />
          <span>🎙️ టెస్ట్ వాయిస్: రమేష్ కి 1000 కట్టాలి</span>
        </button>

        {quickActions.map((qa, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(qa.prompt, false)}
            disabled={isProcessing}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '20px',
              padding: '6px 14px',
              fontSize: '0.78rem',
              fontWeight: 600,
              color: 'var(--text-main)',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = qa.color;
              e.currentTarget.style.background = 'var(--bg-card-subtle)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-color)';
              e.currentTarget.style.background = 'var(--bg-card)';
            }}
          >
            <span style={{ color: qa.color }}>{qa.label}</span>
          </button>
        ))}
      </div>

      {/* Bottom Accessible Voice & Text Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (isRecording) {
            hasSubmittedThisTurnRef.current = true;
            if (recognitionRef.current) {
              try { recognitionRef.current.abort(); } catch (err) {}
            }
            setIsRecording(false);
          }
          const textToSend = inputText.trim() || transcriptRef.current.trim();
          if (textToSend) {
            handleSendMessage(textToSend, false);
          }
        }}
        style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--bg-card)', padding: '10px 14px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-color)' }}
      >
        {/* Big Glowing Microphone Button */}
        <button
          type="button"
          onClick={toggleRecording}
          disabled={isProcessing}
          className={`btn ${isRecording ? 'mic-active' : 'btn-primary'}`}
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            padding: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            background: isRecording ? 'var(--payable-color)' : 'linear-gradient(135deg, #0284C7, #06B6D4)',
            boxShadow: isRecording ? '0 0 20px rgba(239, 68, 68, 0.7)' : '0 4px 12px rgba(6, 182, 212, 0.35)'
          }}
          title={isRecording ? "Click to stop recording and send" : "మైక్ పై నొక్కి మాట్లాడండి (Tap to Speak Voice Prompt)"}
        >
          {isRecording ? <MicOff size={22} /> : <Mic size={22} />}
        </button>

        {/* Speech Language Switcher Toggle */}
        <button
          type="button"
          onClick={() => setSpeechLang(prev => prev === 'te-IN' ? 'en-IN' : 'te-IN')}
          style={{
            background: 'var(--bg-card-subtle)',
            border: '1px solid var(--border-color)',
            borderRadius: '16px',
            padding: '5px 10px',
            fontSize: '0.72rem',
            fontWeight: 700,
            color: 'var(--cyan)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            flexShrink: 0
          }}
          title="Switch Voice Recognition Language (Telugu / English)"
        >
          <span>🗣️ {speechLang === 'te-IN' ? 'తెలుగు (te-IN)' : 'English (en-IN)'}</span>
        </button>

        {/* Text Input */}
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="మాట్లాడండి లేదా టైప్ చేయండి (ఉదా: 'Supplier ki 5000 ivvali' / 'రమేష్ కి 1000 ఇచ్చేశాను')..."
          disabled={isProcessing}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            color: 'var(--text-main)',
            fontSize: '0.95rem',
            outline: 'none',
            padding: '8px 10px'
          }}
        />

        {/* Send Button */}
        <button
          type="submit"
          disabled={isProcessing || !inputText.trim()}
          className="btn btn-primary"
          style={{
            padding: '10px 18px',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontWeight: 600
          }}
        >
          <Send size={16} /> Send
        </button>
      </form>

      {/* Contradiction Modal */}
      <ContradictionModal
        isOpen={isContradictionModalOpen}
        onClose={() => setIsContradictionModalOpen(false)}
        onConfirm={handleConfirmContradiction}
        data={contradictionData}
      />

      {/* Disambiguation Modal */}
      <DisambiguationModal
        isOpen={isDisambiguationModalOpen}
        onClose={() => setIsDisambiguationModalOpen(false)}
        onSelectExisting={handleSelectExistingEntity}
        onCreateNew={handleCreateNewEntity}
        data={disambiguationData}
      />

      {/* Edit & Delete Transaction Modal */}
      <EditTransactionModal
        isOpen={isEditTxModalOpen}
        onClose={() => setIsEditTxModalOpen(false)}
        transaction={selectedTxForEdit}
        onSaved={handleTransactionSavedInChat}
        onDeleted={handleTransactionDeletedInChat}
      />
    </div>
  );
};
