import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Mic,
  MicOff,
  Trash2,
  Bot,
  User,
  CheckCircle,
  Layers,
  RotateCcw,
  History,
  MessageSquare,
  X,
  Plus,
  Edit3,
  Wifi,
  WifiOff,
  Cpu,
  Volume2,
  VolumeX,
  Sparkles,
  CheckCheck,
  TrendingUp,
  Calendar,
  DollarSign,
  AlertCircle
} from 'lucide-react';
import { api, SpokenTextResponse } from '../api/client';
import { PipelineVisualizer } from '../components/PipelineVisualizer';
import { ContradictionModal } from '../components/ContradictionModal';
import { DisambiguationModal } from '../components/DisambiguationModal';
import { DiscrepancyCard } from '../components/DiscrepancyCard';
import { DisambiguationCard } from '../components/DisambiguationCard';
import { EditTransactionModal } from '../components/EditTransactionModal';
import { notifyLedgerUpdated } from '../utils/events';
import { useLanguage } from '../context/LanguageContext';
import { speakVernacularFeedback, playAudioCue, createVoiceActivityDetector, VoiceActivityDetector } from '../utils/audio';
import { offlineQueue } from '../utils/offlineQueue';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'system';
  text: string;
  isVoice?: boolean;
  isWelcome?: boolean;
  isError?: boolean;
  isOfflineQueued?: boolean;
  messageType?: string;
  ledgerUpdate?: any;
  subEntries?: any[];
  totalClausesExecuted?: number;
  queryData?: any;
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

export const ConversationView: React.FC = () => {
  const { language, speechCode, t } = useLanguage();

  const getWelcomeText = () => {
    return t(
      'voice.welcome_chat',
      '🙏 **Welcome to your Multilingual Voice FinTech Ledger Assistant!**\n\nSpeak or type naturally in **English, Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, or Gujarati**.'
    );
  };

  const createWelcomeMsg = (): ChatMessage => ({
    id: `welcome_${Date.now()}`,
    sender: 'system',
    text: getWelcomeText(),
    isWelcome: true,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });

  const createInitSession = (): ChatSession => {
    const newId = `session_${Date.now()}`;
    return {
      id: newId,
      title: t('voice.chat_history', 'New Chat'),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [createWelcomeMsg()]
    };
  };

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
    const initial = {
      id: `session_${Date.now()}`,
      title: 'New Chat',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [{
        id: `welcome_${Date.now()}`,
        sender: 'system' as const,
        text: '🙏 **Welcome to your Multilingual Voice FinTech Ledger Assistant!**\n\nSpeak or type naturally in English, Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, or Gujarati.',
        isWelcome: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]
    };
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
  const [offlineNotice, setOfflineNotice] = useState<string | null>(null);

  // Voice Recording State (Dual Mode: Online Cloud STT + Local Offline STT Fallback + VAD)
  const [isRecording, setIsRecording] = useState(false);
  const [isOfflineTranscribing, setIsOfflineTranscribing] = useState(false);
  const [sttMode, setSttMode] = useState<'auto' | 'cloud' | 'offline'>('auto');
  const [activeEngine, setActiveEngine] = useState<'cloud' | 'offline' | null>(null);
  const [liveVoiceTranscript, setLiveVoiceTranscript] = useState('');
  const [speechLang, setSpeechLang] = useState<'en-IN' | 'te-IN' | 'ta-IN' | 'hi-IN' | 'kn-IN' | 'ml-IN' | 'ur-IN' | 'gu-IN'>(speechCode);
  const [ttsEnabled, setTtsEnabled] = useState<boolean>(() => {
    const saved = localStorage.getItem('nlpledger_tts_enabled');
    return saved !== null ? saved === 'true' : true;
  });

  useEffect(() => {
    setSpeechLang(speechCode);
  }, [speechCode]);

  const recognitionRef = useRef<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const vadRef = useRef<VoiceActivityDetector | null>(null);
  const interimIntervalRef = useRef<any>(null);
  const isInterimTranscribingRef = useRef<boolean>(false);
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
        const fresh = createInitSession();
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
    const newSession = createInitSession();
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
      const fresh = createInitSession();
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
    const resetWelcome = createWelcomeMsg();
    setSessions(prev =>
      prev.map(s =>
        s.id === activeSessionId
          ? { ...s, title: 'New Chat', messages: [resetWelcome], updatedAt: new Date().toISOString() }
          : s
      )
    );
    setLatestDiagnostics(null);
    api.resetSession(activeSessionId).catch(err => console.warn(err));
  };

  // Clear all data and reset fresh
  const handleClearAllData = async () => {
    if (window.confirm(t('set.confirm_clear', 'Are you sure you want to clear all ledger data and start completely fresh from scratch?'))) {
      try {
        setIsProcessing(true);
        await api.resetAllLedger();
        const fresh = createInitSession();
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

  // Dual-Mode Voice Handler (Online Web Speech API + Offline Local Faster-Whisper Fallback)
  const isSpeechRecognitionSupported = typeof window !== 'undefined' && !!((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);

  const getEffectiveSttMode = (): 'cloud' | 'offline' => {
    if (sttMode === 'offline') return 'offline';
    if (sttMode === 'cloud') return 'cloud';
    // 'auto' mode: check online status and browser support
    if (!navigator.onLine || !isSpeechRecognitionSupported) return 'offline';
    return 'cloud';
  };

  const toggleRecording = () => {
    if (isRecording) {
      if (activeEngine === 'offline') {
        stopOfflineRecording();
      } else {
        stopRecording();
      }
    } else {
      const mode = getEffectiveSttMode();
      if (mode === 'offline') {
        startOfflineRecording();
      } else {
        startRecording();
      }
    }
  };

  // 1. ONLINE CLOUD RECORDING (Web Speech API + Hands-Free VAD Auto-Stop)
  const startRecording = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Web Speech API not available, falling back to offline audio recorder.");
      startOfflineRecording();
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
      setActiveEngine('cloud');
      playAudioCue('start');

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = speechLang;

      recognition.onstart = () => {
        setIsRecording(true);
        setActiveEngine('cloud');
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
        setActiveEngine(null);
        if (vadRef.current) {
          vadRef.current.stop();
          vadRef.current = null;
        }
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
        if (event.error === 'network') {
          setOfflineNotice("⚡ Network disconnected: Seamlessly switched to 100% Offline Local faster-whisper STT.");
          setIsRecording(false);
          setActiveEngine(null);
          startOfflineRecording();
          return;
        }
        if (event.error !== 'no-speech') {
          setIsRecording(false);
          setActiveEngine(null);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();

      // Initialize Web Audio API VAD for hands-free 1.2s silence detection
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
          mediaStreamRef.current = stream;
          vadRef.current = createVoiceActivityDetector(
            stream,
            () => {
              if (transcriptRef.current.trim() && !hasSubmittedThisTurnRef.current) {
                stopRecording();
              }
            },
            1200
          );
        }).catch(err => console.warn("VAD init warning:", err));
      }
    } catch (e) {
      console.error("Speech recognition startup error:", e);
      startOfflineRecording();
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    setActiveEngine(null);
    if (vadRef.current) {
      vadRef.current.stop();
      vadRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(t => t.stop());
      mediaStreamRef.current = null;
    }
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

  // 2. OFFLINE LOCAL RECORDING (MediaRecorder + faster-whisper real-time streaming + VAD)
  const startOfflineRecording = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Microphone access is not supported in this browser context.");
        return;
      }

      transcriptRef.current = '';
      hasSubmittedThisTurnRef.current = false;
      audioChunksRef.current = [];
      setLiveVoiceTranscript('');
      setIsRecording(true);
      setActiveEngine('offline');
      playAudioCue('start');

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : 'audio/mp4';

      const recorder = new MediaRecorder(stream, { mimeType });
      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      // Periodic Live Interim Transcription Stream (every 1.4 seconds)
      if (interimIntervalRef.current) clearInterval(interimIntervalRef.current);
      interimIntervalRef.current = setInterval(async () => {
        if (audioChunksRef.current.length >= 3 && !isInterimTranscribingRef.current && mediaRecorderRef.current?.state === 'recording') {
          isInterimTranscribingRef.current = true;
          try {
            const interimBlob = new Blob(audioChunksRef.current, { type: mimeType });
            const langPrefix = speechLang.split('-')[0];
            const interimRes = await api.transcribeOfflineAudio(interimBlob, langPrefix, true);
            if (interimRes.text && interimRes.text.trim()) {
              const partial = interimRes.text.trim();
              transcriptRef.current = partial;
              setLiveVoiceTranscript(partial);
            }
          } catch (e) {
            // Silently ignore interim chunk network glitches
          } finally {
            isInterimTranscribingRef.current = false;
          }
        }
      }, 1400);

      // Attach Web Audio API VAD for hands-free 1.2s silence auto-stop
      vadRef.current = createVoiceActivityDetector(
        stream,
        () => {
          if (audioChunksRef.current.length >= 2 && !hasSubmittedThisTurnRef.current) {
            stopOfflineRecording();
          }
        },
        1200
      );

      recorder.onstop = async () => {
        if (interimIntervalRef.current) {
          clearInterval(interimIntervalRef.current);
          interimIntervalRef.current = null;
        }
        if (vadRef.current) {
          vadRef.current.stop();
          vadRef.current = null;
        }

        // Clean up audio tracks
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach(track => track.stop());
          mediaStreamRef.current = null;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        if (audioBlob.size < 500) {
          setIsOfflineTranscribing(false);
          setLiveVoiceTranscript('');
          return;
        }

        setIsOfflineTranscribing(true);

        try {
          const langPrefix = speechLang.split('-')[0];
          const res = await api.transcribeOfflineAudio(audioBlob, langPrefix, false);
          const transcribedText = res.text ? res.text.trim() : (transcriptRef.current.trim() || '');

          setIsOfflineTranscribing(false);
          setLiveVoiceTranscript('');

          if (transcribedText) {
            transcriptRef.current = transcribedText;
            hasSubmittedThisTurnRef.current = true;
            handleSendMessage(transcribedText, true);
          } else {
            setOfflineNotice("ℹ️ No clear speech detected in offline recording. Please try speaking again.");
          }
        } catch (err: any) {
          console.error("Offline transcription error:", err);
          setIsOfflineTranscribing(false);
          setLiveVoiceTranscript('');
          setOfflineNotice(`⚠️ Offline STT Error: ${err.message || 'Failed to process audio'}`);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250);
    } catch (err: any) {
      console.error("Microphone capture error:", err);
      setIsRecording(false);
      setActiveEngine(null);
      alert("Microphone permission denied or audio device not found.");
    }
  };

  const stopOfflineRecording = () => {
    setIsRecording(false);
    setActiveEngine(null);
    if (vadRef.current) {
      vadRef.current.stop();
      vadRef.current = null;
    }
    if (interimIntervalRef.current) {
      clearInterval(interimIntervalRef.current);
      interimIntervalRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch (e) {
        console.warn("MediaRecorder stop error:", e);
      }
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
          const isDefaultTitle = s.title.includes('కొత్త సంభాషణ') || s.title.includes('New Chat') || s.title.includes('புதிய') || s.title.includes('नई');
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

    // If device is strictly offline, enqueue locally for auto-sync
    if (!navigator.onLine) {
      offlineQueue.enqueue(trimmed, targetSessionId, isVoice);
      playAudioCue('success');
      const queueMsg: ChatMessage = {
        id: `queue_${Date.now()}`,
        sender: 'system',
        text: `⚡ **Offline Mode Active**: Transaction queued locally. It will automatically synchronize to your ledger once network connection is restored.`,
        isOfflineQueued: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setSessions(prev =>
        prev.map(s =>
          s.id === targetSessionId
            ? { ...s, messages: [...s.messages, queueMsg] }
            : s
        )
      );
      isSendingRef.current = false;
      return;
    }

    setIsProcessing(true);

    try {
      const response: SpokenTextResponse = isVoice
        ? await api.processSpokenText(trimmed, targetSessionId)
        : await api.sendMessage(trimmed, targetSessionId);

      handleProcessResponse(response, targetSessionId);
    } catch (err: any) {
      console.warn("Send message error:", err);
      // If network fetch failed, enqueue for offline sync
      if (!navigator.onLine || err.message?.includes('Failed to fetch') || err.message?.includes('NetworkError')) {
        offlineQueue.enqueue(trimmed, targetSessionId, isVoice);
        const offlineMsg: ChatMessage = {
          id: `sys_off_${Date.now()}`,
          sender: 'system',
          text: `📡 **Network Connection Offline**: Transaction queued locally in browser storage. Will automatically sync to database when reconnected.`,
          isOfflineQueued: true,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setSessions(prev =>
          prev.map(s =>
            s.id === targetSessionId
              ? { ...s, messages: [...s.messages, offlineMsg] }
              : s
          )
        );
      } else {
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
      }
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

    // Hands-Free Vernacular TTS Audio Vocalization
    if (ttsEnabled && response.text_response) {
      speakVernacularFeedback(response.text_response, speechLang);
    }

    const botMsg: ChatMessage = {
      id: `bot_${Date.now()}`,
      sender: 'system',
      text: response.text_response,
      messageType: response.message_type,
      ledgerUpdate: response.ledger_update,
      subEntries: response.sub_entries,
      totalClausesExecuted: response.total_clauses_executed,
      queryData: response.query_data,
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

  const getCancelledContradictionText = () => {
    if (language === 'te') return '⚠️ **లావాదేవీ రద్దు చేయబడింది.** లెక్కల పుస్తకంలో ఎలాంటి మార్పు జరగలేదు.';
    if (language === 'ta') return '⚠️ **பரிவர்த்தனை ரத்து செய்யப்பட்டது.** கணக்கு புத்தகத்தில் எந்த மாற்றமும் செய்யப்படவில்லை.';
    if (language === 'hi') return '⚠️ **लेन-देन रद्द कर दिया गया।** बहीखाते में कोई बदलाव नहीं किया गया।';
    return '⚠️ **Transaction cancelled.** No changes were made to the ledger.';
  };

  const handleCancelContradiction = (customData?: any) => {
    setIsContradictionModalOpen(false);
    setContradictionData(null);
    const cancelMsg: ChatMessage = {
      id: `bot_cancel_${Date.now()}`,
      sender: 'system',
      text: getCancelledContradictionText(),
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

  const getCancelledDisambiguationText = () => {
    if (language === 'te') return '⚠️ **ఖాతా ఎంపిక రద్దు చేయబడింది.** ఎలాంటి ఖాతా అనుసంధానం జరగలేదు.';
    if (language === 'ta') return '⚠️ **கணக்கு தேர்வு ரத்து செய்யப்பட்டது.** எந்த கணக்கும் இணைக்கப்படவில்லை.';
    if (language === 'hi') return '⚠️ **खाता चयन रद्द कर दिया गया।** कोई खाता लिंक नहीं किया गया।';
    return '⚠️ **Account selection cancelled.** No link was established.';
  };

  const handleCancelDisambiguation = (customData?: any) => {
    setIsDisambiguationModalOpen(false);
    setDisambiguationData(null);
    const cancelMsg: ChatMessage = {
      id: `bot_cancel_disamb_${Date.now()}`,
      sender: 'system',
      text: getCancelledDisambiguationText(),
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
                {t('nav.conversation', 'Voice & Text Ledger')}
              </h2>
              <span className="badge badge-emerald" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                🟢 Live
              </span>
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              {t('app.subtitle', 'Multilingual Voice FinTech Khata')}
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
            <span>{t('voice.start_new', '+ Start New Chat')}</span>
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
            <span>{t('voice.chat_history', 'Chat History')} ({sessions.length})</span>
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
            <span>{t('voice.clear_chat', 'Clear Chat')}</span>
          </button>

          {/* RESET BOOK */}
          <button
            onClick={handleClearAllData}
            className="btn btn-danger-subtle"
            title="Wipe test data and start fresh with empty book"
          >
            <RotateCcw size={16} />
            <span>{t('voice.reset_book', 'Reset Book')}</span>
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
              <History size={16} color="var(--cyan)" /> {t('voice.chat_history', 'Chat History')}
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
              <Plus size={15} /> {t('voice.start_new', '+ Start New Chat')}
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
                  {m.ledgerUpdate && (() => {
                    const lu = m.ledgerUpdate;
                    const txType = (lu.transaction_type || '').toUpperCase();
                    const status = (lu.status || '').toUpperCase();
                    const direction = (lu.direction || '').toLowerCase();
                    const entityType = (lu.entity_type || '').toLowerCase();

                    let catType: 'PAYABLE' | 'RECEIVABLE' | 'PAID' | 'RECEIVED' = 'RECEIVABLE';
                    let catLabel = `🟢 ${t('term.receivable', 'Receivable (To Receive)')}`;
                    let catBadgeClass = 'badge-emerald';
                    let catColor = 'var(--receivable-color)';
                    let catBg = 'var(--receivable-light)';
                    let catBorder = '1px solid var(--receivable-border)';
                    let flowTag = 'Incoming Due / Asset';

                    if (
                      txType === 'PAYMENT_MADE' ||
                      (entityType === 'supplier' && (txType.includes('PAYMENT') || status === 'SETTLED' || status === 'PARTIAL_PAYMENT'))
                    ) {
                      catType = 'PAID';
                      catLabel = `💸 ${t('term.paid', 'Paid (Outflow)')}`;
                      catBadgeClass = 'badge-amber';
                      catColor = '#d97706';
                      catBg = 'rgba(245, 158, 11, 0.08)';
                      catBorder = '1px solid rgba(245, 158, 11, 0.35)';
                      flowTag = 'Outflow Settled / Paid';
                    } else if (
                      txType === 'PAYMENT_RECEIVED' ||
                      txType === 'ADVANCE_RECEIVED' ||
                      (entityType === 'customer' && (status === 'PARTIAL_PAYMENT' || status === 'SETTLED' || txType.includes('PAYMENT')))
                    ) {
                      catType = 'RECEIVED';
                      catLabel = `💰 ${t('term.received', 'Received (Inflow)')}`;
                      catBadgeClass = 'badge-cyan';
                      catColor = '#0284c7';
                      catBg = 'rgba(2, 132, 199, 0.08)';
                      catBorder = '1px solid rgba(2, 132, 199, 0.35)';
                      flowTag = 'Inflow Collected / Received';
                    } else if (direction === 'payable' || entityType === 'supplier' || txType === 'PURCHASE' || txType === 'PAYABLE_INVOICE') {
                      catType = 'PAYABLE';
                      catLabel = `🔴 ${t('term.payable', 'Payable (To Pay)')}`;
                      catBadgeClass = 'badge-rose';
                      catColor = 'var(--payable-color)';
                      catBg = 'var(--payable-light)';
                      catBorder = '1px solid var(--payable-border)';
                      flowTag = 'Liability / You Owe';
                    }

                    return (
                      <div
                        style={{
                          marginTop: '12px',
                          padding: '14px 16px',
                          background: lu.is_deleted ? 'rgba(239, 68, 68, 0.08)' : catBg,
                          borderRadius: 'var(--radius-md)',
                          border: lu.is_deleted ? '1px dashed #ef4444' : catBorder,
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '6px',
                          opacity: lu.is_deleted ? 0.75 : 1
                        }}
                      >
                        {lu.is_deleted ? (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#dc2626', fontSize: '0.85rem', fontWeight: 600 }}>
                            <Trash2 size={16} />
                            <span>Transaction Deleted & Balance Rolled Back</span>
                          </div>
                        ) : (
                          <>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span
                                  className={`badge ${catBadgeClass}`}
                                  style={{ fontSize: '0.78rem', fontWeight: 700, padding: '3px 10px' }}
                                >
                                  {catLabel}
                                </span>
                                <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', background: 'var(--bg-card)', padding: '2px 6px', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                                  {flowTag}
                                </span>
                                {lu.is_edited && (
                                  <span className="badge badge-amber" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>
                                    ✏️ {t('btn.edit', 'Edited')}
                                  </span>
                                )}
                              </div>
                              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                                Tx #{lu.transaction_id || 'LOGGED'}
                              </span>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginTop: '4px' }}>
                              <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                                {lu.actor}
                              </span>
                              <span style={{ fontSize: '1.3rem', fontWeight: 800, color: catColor }}>
                                ₹{Number(lu.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                              </span>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px dashed var(--border-color)', paddingTop: '6px', marginTop: '2px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                              <span>{t('term.balance', 'Current Balance')}:</span>
                              <strong style={{ color: 'var(--text-main)', fontSize: '0.9rem' }}>
                                ₹{Number(lu.current_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                              </strong>
                            </div>

                            {/* Inline Edit & Delete Actions */}
                            {lu.transaction_id && (
                              <div style={{ display: 'flex', gap: '8px', marginTop: '8px', borderTop: '1px solid var(--border-color)', paddingTop: '8px', justifyContent: 'flex-end' }}>
                                <button
                                  type="button"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedTxForEdit({
                                      id: lu.transaction_id,
                                      counterparty_name: lu.actor,
                                      amount: lu.amount,
                                      direction: lu.direction || (lu.entity_type === 'supplier' ? 'payable' : 'receivable'),
                                      transaction_type: lu.transaction_type || (lu.entity_type === 'supplier' ? 'PURCHASE' : 'CREDIT_SALE'),
                                      payment_method: lu.payment_method || 'cash',
                                      date: lu.date || new Date().toISOString().split('T')[0]
                                    });
                                    setIsEditTxModalOpen(true);
                                  }}
                                  className="btn btn-secondary"
                                  style={{ padding: '4px 10px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
                                >
                                  <Edit3 size={13} /> {t('btn.edit', 'Edit')}
                                </button>
                                <button
                                  type="button"
                                  onClick={async (e) => {
                                    e.stopPropagation();
                                    if (window.confirm(t('tx.confirm_delete', 'Are you sure you want to delete this transaction?'))) {
                                      try {
                                        await api.deleteTransaction(lu.transaction_id);
                                        handleTransactionDeletedInChat(lu.transaction_id);
                                      } catch (err: any) {
                                        alert("Error deleting transaction: " + err.message);
                                      }
                                    }
                                  }}
                                  className="btn btn-danger-subtle"
                                  style={{ padding: '4px 10px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
                                >
                                  <Trash2 size={13} /> {t('btn.delete', 'Delete')}
                                </button>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    );
                  })()}

                  {/* One-Breath Composite Multi-Transaction Card */}
                  {m.subEntries && m.subEntries.length > 0 && (
                    <div
                      style={{
                        marginTop: '12px',
                        padding: '14px 16px',
                        background: 'rgba(2, 132, 199, 0.08)',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid rgba(2, 132, 199, 0.3)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '10px'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.88rem', color: 'var(--cyan)' }}>
                          <Layers size={16} />
                          <span>⚡ {t('voice.batch_ingested', 'One-Breath Multi-Transaction Batch')} ({m.subEntries.length} entries)</span>
                        </div>
                        <span className="badge badge-emerald" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                          ✓ 100% Ingested
                        </span>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {m.subEntries.map((sub: any, idx: number) => {
                          const ev = sub.event || {};
                          const lu = sub.ledger_update || {};
                          const txType = (lu.transaction_type || ev.event_type || '').toUpperCase();
                          const isPayable = ev.direction === 'payable' || lu.entity_type === 'supplier';
                          const isPaymentMade = isPayable && (txType.includes('PAYMENT') || lu.status === 'SETTLED');
                          const isPaymentRecv = !isPayable && (txType.includes('PAYMENT') || txType.includes('RECEIVED') || lu.status === 'PARTIAL_PAYMENT');

                          let subBadge = `🟢 ${t('term.receivable', 'Receivable')}`;
                          let subClass = 'badge-emerald';
                          let subColor = 'var(--receivable-color)';
                          let subBg = 'rgba(16, 185, 129, 0.06)';
                          let subBorder = '1px solid var(--receivable-border)';

                          if (isPaymentMade) {
                            subBadge = `💸 ${t('term.paid', 'Paid')}`;
                            subClass = 'badge-amber';
                            subColor = '#d97706';
                            subBg = 'rgba(245, 158, 11, 0.06)';
                            subBorder = '1px solid rgba(245, 158, 11, 0.3)';
                          } else if (isPaymentRecv) {
                            subBadge = `💰 ${t('term.received', 'Received')}`;
                            subClass = 'badge-cyan';
                            subColor = '#0284c7';
                            subBg = 'rgba(2, 132, 199, 0.06)';
                            subBorder = '1px solid rgba(2, 132, 199, 0.3)';
                          } else if (isPayable) {
                            subBadge = `🔴 ${t('term.payable', 'Payable')}`;
                            subClass = 'badge-rose';
                            subColor = 'var(--payable-color)';
                            subBg = 'rgba(239, 68, 68, 0.06)';
                            subBorder = '1px solid var(--payable-border)';
                          }

                          return (
                            <div
                              key={idx}
                              style={{
                                padding: '8px 12px',
                                borderRadius: '8px',
                                background: subBg,
                                border: subBorder,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                fontSize: '0.85rem'
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span className={`badge ${subClass}`} style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                                  {subBadge}
                                </span>
                                <strong style={{ color: 'var(--text-main)' }}>{ev.actor}</strong>
                                <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>({sub.clause})</span>
                              </div>
                              <div style={{ textAlign: 'right' }}>
                                <span style={{ fontWeight: 800, color: subColor }}>
                                  ₹{Number(ev.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                                </span>
                                {lu.current_balance !== undefined && (
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                    Bal: ₹{Number(lu.current_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Voice CFO Analytical Intelligence Card */}
                  {m.queryData && typeof m.queryData === 'object' && Object.keys(m.queryData).length > 0 && (
                    <div
                      style={{
                        marginTop: '12px',
                        padding: '14px 16px',
                        background: 'linear-gradient(135deg, rgba(2, 132, 199, 0.08), rgba(16, 185, 129, 0.08))',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--border-color)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.88rem', color: 'var(--cyan)' }}>
                        <Sparkles size={16} />
                        <span>🎙️ Voice CFO Financial Intelligence</span>
                      </div>

                      {/* Metric Highlights */}
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '4px' }}>
                        {m.queryData.entity_name && m.queryData.total_amount !== undefined && (
                          <div style={{ padding: '6px 12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid var(--payable-border)', fontSize: '0.8rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Top Payout: </span>
                            <strong style={{ color: 'var(--payable-color)' }}>{m.queryData.entity_name} (₹{Number(m.queryData.total_amount || 0).toLocaleString('en-IN')})</strong>
                          </div>
                        )}
                        {m.queryData.today_collections !== undefined && (
                          <div style={{ padding: '6px 12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid var(--receivable-border)', fontSize: '0.8rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Collections: </span>
                            <strong style={{ color: 'var(--receivable-color)' }}>₹{Number(m.queryData.today_collections).toLocaleString('en-IN')}</strong>
                          </div>
                        )}
                        {m.queryData.today_payouts !== undefined && (
                          <div style={{ padding: '6px 12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid var(--payable-border)', fontSize: '0.8rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Payouts: </span>
                            <strong style={{ color: 'var(--payable-color)' }}>₹{Number(m.queryData.today_payouts).toLocaleString('en-IN')}</strong>
                          </div>
                        )}
                        {m.queryData.total_weekly_receivables !== undefined && (
                          <div style={{ padding: '6px 12px', background: 'rgba(2, 132, 199, 0.1)', borderRadius: '8px', border: '1px solid rgba(2, 132, 199, 0.3)', fontSize: '0.8rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>This Week Dues: </span>
                            <strong style={{ color: 'var(--cyan)' }}>₹{Number(m.queryData.total_weekly_receivables).toLocaleString('en-IN')}</strong>
                          </div>
                        )}
                        {m.queryData.total_receivables !== undefined && (
                          <div style={{ padding: '6px 12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid var(--receivable-border)', fontSize: '0.8rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Total Receivables: </span>
                            <strong style={{ color: 'var(--receivable-color)' }}>₹{Number(m.queryData.total_receivables).toLocaleString('en-IN')}</strong>
                          </div>
                        )}
                        {m.queryData.total_payables !== undefined && (
                          <div style={{ padding: '6px 12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid var(--payable-border)', fontSize: '0.8rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Total Payables: </span>
                            <strong style={{ color: 'var(--payable-color)' }}>₹{Number(m.queryData.total_payables).toLocaleString('en-IN')}</strong>
                          </div>
                        )}
                      </div>
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
        {(isRecording || isOfflineTranscribing) && (
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
                background: activeEngine === 'offline' || isOfflineTranscribing
                  ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(16, 185, 129, 0.12))'
                  : 'linear-gradient(135deg, rgba(2, 132, 199, 0.15), rgba(16, 185, 129, 0.12))',
                border: activeEngine === 'offline' || isOfflineTranscribing
                  ? '1.5px solid #F59E0B'
                  : '1.5px solid var(--cyan)',
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
                  <div style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: isOfflineTranscribing ? '#F59E0B' : 'var(--payable-color)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    animation: 'pulseGlow 1.2s infinite'
                  }}>
                    {isOfflineTranscribing ? <Cpu size={16} /> : <Mic size={16} />}
                  </div>
                  <div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: activeEngine === 'offline' || isOfflineTranscribing ? '#F59E0B' : 'var(--cyan)' }}>
                      {isOfflineTranscribing
                        ? t('voice.transcribing_local', 'Transcribing on Local CPU (faster-whisper)...')
                        : activeEngine === 'offline'
                        ? t('voice.recording_offline_badge', '🔒 100% Offline Local Voice')
                        : t('header.listening', '⚡ Live Cloud Speech Stream')}
                    </span>
                  </div>
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
              <div style={{ fontSize: '1.02rem', color: liveVoiceTranscript ? 'var(--text-main)' : 'var(--text-muted)', fontStyle: liveVoiceTranscript ? 'normal' : 'italic', fontWeight: liveVoiceTranscript ? 600 : 400, minHeight: '28px', display: 'flex', alignItems: 'center' }}>
                {liveVoiceTranscript ? (
                  <span>
                    "{liveVoiceTranscript}"
                    <span style={{ display: 'inline-block', width: '7px', height: '14px', background: activeEngine === 'offline' ? '#F59E0B' : 'var(--cyan)', marginLeft: '4px', verticalAlign: 'middle', animation: 'blink 0.9s infinite ease-in-out' }} />
                  </span>
                ) : (
                  <span>{activeEngine === 'offline' ? '🎙️ Listening offline... Speak your transaction' : t('header.listening', 'Listening... Speak now')}</span>
                )}
              </div>

              {/* Action Button on Live Card */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px', borderTop: '1px solid var(--border-color)', paddingTop: '8px', marginTop: '2px' }}>
                <button
                  type="button"
                  onClick={toggleRecording}
                  disabled={isOfflineTranscribing}
                  style={{
                    background: liveVoiceTranscript && activeEngine !== 'offline' ? 'linear-gradient(135deg, #10B981, #059669)' : 'var(--payable-color)',
                    border: 'none',
                    borderRadius: '20px',
                    padding: '5px 14px',
                    color: '#fff',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: isOfflineTranscribing ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                  }}
                >
                  <CheckCircle size={14} /> {activeEngine === 'offline' ? t('voice.finish_recording', 'Stop & Transcribe') : (liveVoiceTranscript ? t('voice.send', 'Send') : t('voice.stop_recording', 'Stop'))}
                </button>
              </div>
            </div>

            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: activeEngine === 'offline' ? 'linear-gradient(135deg, #D97706, #F59E0B)' : 'linear-gradient(135deg, #0284C7, #06B6D4)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', flexShrink: 0, border: '1px solid var(--border-color)', marginTop: '2px' }}>
              {activeEngine === 'offline' ? <Cpu size={18} /> : <Mic size={18} />}
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
              <span>{t('voice.thinking', 'Multilingual NLP is processing speech & double-entry state...')}</span>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Offline Speech Notice Banner */}
      {offlineNotice && (
        <div
          style={{
            background: 'rgba(234, 88, 12, 0.12)',
            border: '1px solid rgba(234, 88, 12, 0.35)',
            borderRadius: 'var(--radius-md)',
            padding: '10px 14px',
            fontSize: '0.8rem',
            color: '#EA580C',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '8px'
          }}
        >
          <span>{offlineNotice}</span>
          <button
            onClick={() => setOfflineNotice(null)}
            style={{ background: 'transparent', border: 'none', color: '#EA580C', cursor: 'pointer', fontWeight: 700 }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Quick Access Vernacular Voice Suggestion Chips for All 8 Languages */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '10px', scrollbarWidth: 'none' }}>
        {(
          language === 'te'
            ? [
                { label: '🎙️ రమేష్ కి 1000 ఇచ్చేశాను', prompt: 'రమేష్ కి 1000 ఇచ్చేశాను', color: 'var(--cyan)' },
                { label: '🎙️ రమేష్ నుండి 2500 రావాలి', prompt: 'రమేష్ నుండి 2500 రావాలి', color: 'var(--jama-green)' },
                { label: '🎙️ ఈ వారం రావాల్సిన బాకీలు ఎంత?', prompt: 'ఈ వారం మొత్తం రావాల్సిన బాకీలు ఎంత?', color: 'var(--udhaar-red)' }
              ]
            : language === 'ta'
            ? [
                { label: '🎙️ செல்வத்துக்கு 2000 கொடுக்கனும்', prompt: 'செல்வத்துக்கு 2000 கொடுக்கனும்', color: 'var(--udhaar-red)' },
                { label: '🎙️ முருகன் 1500 கொடுத்தார்', prompt: 'முருகன் 1500 கொடுத்தார்', color: 'var(--jama-green)' },
                { label: '🎙️ இந்த வாரம் வர வேண்டிய பாக்கிகள்?', prompt: 'இந்த வாரம் வர வேண்டிய பாக்கிகள் எவ்வளவு?', color: 'var(--cyan)' }
              ]
            : language === 'hi'
            ? [
                { label: '🎙️ राहुल को 5000 देना है', prompt: 'राहुल को 5000 देना है', color: 'var(--udhaar-red)' },
                { label: '🎙️ अमित ने 1500 जमा किया', prompt: 'अमित ने 1500 जमा किया', color: 'var(--jama-green)' },
                { label: '🎙️ इस महीने सबसे ज्यादा भुगतान किसे किया?', prompt: 'इस महीने सबसे ज्यादा भुगतान किसे किया?', color: 'var(--cyan)' }
              ]
            : language === 'kn'
            ? [
                { label: '🎙️ ಸುರೇಶ್‌ಗೆ 2000 ಕೊಟ್ಟೆ', prompt: 'ಸುರೇಶ್‌ಗೆ 2000 ಕೊಟ್ಟೆ', color: 'var(--udhaar-red)' },
                { label: '🎙️ ರಮೇಶ್‌ನಿಂದ 1500 ಬರಬೇಕು', prompt: 'ರಮೇಶ್‌ನಿಂದ 1500 ಬರಬೇಕು', color: 'var(--jama-green)' },
                { label: '🎙️ ಈ ವಾರದ ಬಾಕಿ ವಿವರಗಳು ತಿಳಿಸಿ', prompt: 'ಈ ವಾರದ ಬಾಕಿ ವಿವರಗಳು ತಿಳಿಸಿ', color: 'var(--cyan)' }
              ]
            : language === 'ml'
            ? [
                { label: '🎙️ രമേശിന് 2000 കൊടുത്തു', prompt: 'രമേശിന് 2000 കൊടുത്തു', color: 'var(--udhaar-red)' },
                { label: '🎙️ സുരേഷിൽ നിന്ന് 1500 വരാനുണ്ട്', prompt: 'സുരേഷിൽ നിന്ന് 1500 വരാനുണ്ട്', color: 'var(--jama-green)' },
                { label: '🎙️ ഈ മാസം കൂടുതൽ നൽകിയത് ആർക്കാണ്?', prompt: 'ഈ മാസം കൂടുതൽ നൽകിയത് ആർക്കാണ്?', color: 'var(--cyan)' }
              ]
            : language === 'ur'
            ? [
                { label: '🎙️ زاہد کو 2000 دیا', prompt: 'زاہد کو 2000 دیا', color: 'var(--udhaar-red)' },
                { label: '🎙️ عمران سے 1500 لینا ہے', prompt: 'عمران سے 1500 لینا ہے', color: 'var(--jama-green)' },
                { label: '🎙️ آج کا کل کیش فلو کتنا ہے؟', prompt: 'آج کا کل کیش فلو کتنا ہے؟', color: 'var(--cyan)' }
              ]
            : language === 'gu'
            ? [
                { label: '🎙️ રમેશને 2000 આપ્યા', prompt: 'રમેશને 2000 આપ્યા', color: 'var(--udhaar-red)' },
                { label: '🎙️ સુરેશ પાસેથી 1500 લેવાના છે', prompt: 'સુરેશ પાસેથી 1500 લેવાના છે', color: 'var(--jama-green)' },
                { label: '🎙️ આ અઠવાડિયે બાકી રકમ કેટલી છે?', prompt: 'આ અઠવાડિયે બાકી રકમ કેટલી છે?', color: 'var(--cyan)' }
              ]
            : [
                { label: '🎙️ Paid 2000 to Ramesh and got 1500 from Suresh', prompt: 'Paid 2000 to Ramesh, received 1500 from Suresh', color: 'var(--cyan)' },
                { label: '🎙️ Who did I pay the most this month?', prompt: 'Who did I pay the most this month?', color: 'var(--udhaar-red)' },
                { label: "🎙️ What are today's total collections and payouts?", prompt: "What are today's total collections and payouts?", color: 'var(--jama-green)' }
              ]
        ).map((qa, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(qa.prompt, true)}
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
          title={isRecording ? t('voice.stop_recording', 'Stop Recording') : t('voice.tap_to_speak', 'Tap to Speak')}
        >
          {isRecording ? <MicOff size={22} /> : <Mic size={22} />}
        </button>

        {/* Vernacular Speech Language Switcher Select (All 8 Languages) */}
        <select
          value={speechLang}
          onChange={(e) => setSpeechLang(e.target.value as any)}
          style={{
            background: 'var(--bg-card-subtle)',
            border: '1px solid var(--cyan)',
            borderRadius: '14px',
            padding: '4px 8px',
            fontSize: '0.72rem',
            fontWeight: 700,
            color: 'var(--cyan)',
            cursor: 'pointer',
            flexShrink: 0
          }}
          title="Switch Voice Recognition Language (English, Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, Gujarati)"
        >
          <option value="en-IN">🇬🇧 English</option>
          <option value="te-IN">🇮🇳 Telugu (తెలుగు)</option>
          <option value="ta-IN">🇮🇳 Tamil (தமிழ்)</option>
          <option value="hi-IN">🇮🇳 Hindi (हिन्दी)</option>
          <option value="kn-IN">🇮🇳 Kannada (ಕನ್ನಡ)</option>
          <option value="ml-IN">🇮🇳 Malayalam (മലയാളം)</option>
          <option value="ur-IN">🇮🇳 Urdu (اردو)</option>
          <option value="gu-IN">🇮🇳 Gujarati (ગુજરાતી)</option>
        </select>

        {/* STT Engine Mode Switcher (Auto Fallback / Cloud / 100% Local Offline) */}
        <select
          value={sttMode}
          onChange={(e) => setSttMode(e.target.value as any)}
          style={{
            background: getEffectiveSttMode() === 'offline' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(6, 182, 212, 0.12)',
            border: getEffectiveSttMode() === 'offline' ? '1px solid #F59E0B' : '1px solid var(--cyan)',
            borderRadius: '14px',
            padding: '4px 8px',
            fontSize: '0.72rem',
            fontWeight: 700,
            color: getEffectiveSttMode() === 'offline' ? '#F59E0B' : 'var(--cyan)',
            cursor: 'pointer',
            flexShrink: 0
          }}
          title="STT Engine: Auto (online cloud + local fallback), Force Cloud Web Speech, or Force 100% Offline Local faster-whisper"
        >
          <option value="auto">⚡ STT: Auto ({getEffectiveSttMode() === 'offline' ? 'Offline' : 'Cloud'})</option>
          <option value="cloud">☁️ Cloud (Web Speech)</option>
          <option value="offline">🔒 100% Offline Local</option>
        </select>

        {/* Spoken Voice TTS Audio Output Toggle */}
        <button
          type="button"
          onClick={() => {
            const next = !ttsEnabled;
            setTtsEnabled(next);
            try {
              localStorage.setItem('nlpledger_tts_enabled', String(next));
            } catch (e) {}
          }}
          style={{
            background: ttsEnabled ? 'rgba(6, 182, 212, 0.12)' : 'var(--bg-card-subtle)',
            border: ttsEnabled ? '1px solid var(--cyan)' : '1px solid var(--border-color)',
            borderRadius: '14px',
            padding: '6px 10px',
            color: ttsEnabled ? 'var(--cyan)' : 'var(--text-dim)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '0.75rem',
            fontWeight: 700,
            flexShrink: 0
          }}
          title={ttsEnabled ? "🔊 Spoken voice feedback active (Click to mute)" : "🔇 Voice feedback muted (Click to enable)"}
        >
          {ttsEnabled ? <Volume2 size={15} /> : <VolumeX size={15} />}
          <span>{ttsEnabled ? 'TTS On' : 'Muted'}</span>
        </button>

        {/* Text Input */}
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={t('voice.placeholder', 'Speak or type your financial transaction...')}
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
          <Send size={16} /> {t('voice.send', 'Send')}
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
