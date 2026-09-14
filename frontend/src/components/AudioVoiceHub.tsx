import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Sparkles, Play, Radio, CheckCircle, AlertCircle } from 'lucide-react';
import { api, SpokenTextResponse } from '../api/client';

interface AudioVoiceHubProps {
  onProcessResult: (result: SpokenTextResponse, transcript: string) => void;
  isProcessing: boolean;
}

export const AudioVoiceHub: React.FC<AudioVoiceHubProps> = ({ onProcessResult, isProcessing }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState('');
  const [samplePrompts, setSamplePrompts] = useState<any[]>([]);
  const [waveformBars, setWaveformBars] = useState<number[]>(Array(32).fill(20));
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    loadSamplePrompts();
  }, []);

  const loadSamplePrompts = async () => {
    try {
      const prompts = await api.getSamplePrompts();
      setSamplePrompts(prompts);
    } catch (err) {
      console.error('Failed to fetch sample prompts', err);
    }
  };

  const hasSubmittedAudioRef = useRef<boolean>(false);

  // Start / Stop Browser Speech Recognition (Web Speech API)
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
      alert("Web Speech API is not supported in this browser. You can click any sample audio scenario below!");
      return;
    }

    try {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch (e) {}
      }

      hasSubmittedAudioRef.current = false;
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'te-IN'; // Telugu + English mixed recognition

      recognition.onstart = () => {
        setIsRecording(true);
        setLiveTranscript('');
        animateWaveform();
      };

      recognition.onresult = (event: any) => {
        const current = event.resultIndex;
        const transcript = event.results[current][0].transcript;
        setLiveTranscript(transcript);
      };

      recognition.onend = () => {
        setIsRecording(false);
        if (liveTranscript.trim() && !hasSubmittedAudioRef.current) {
          hasSubmittedAudioRef.current = true;
          handleExecuteAudio(liveTranscript);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition notice:", event.error);
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e) {
      console.error(e);
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (e) {}
    }
    setIsRecording(false);
  };

  // Simulated animated audio waveform bars
  const animateWaveform = () => {
    const interval = setInterval(() => {
      setWaveformBars(Array.from({ length: 32 }, () => Math.floor(Math.random() * 50) + 10));
    }, 100);
    setTimeout(() => clearInterval(interval), 5000);
  };

  const handleExecuteAudio = async (text: string) => {
    hasSubmittedAudioRef.current = true;
    animateWaveform();
    try {
      const result = await api.processSpokenText(text);
      onProcessResult(result, text);
    } catch (err: any) {
      alert("Error processing audio: " + err.message);
    }
  };

  return (
    <div className="fin-card" style={{ background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(16, 185, 129, 0.04))', border: '1px solid rgba(6, 182, 212, 0.3)', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h3 style={{ fontSize: '1.25rem', color: '#38BDF8' }}>Voice Recognition & Speech Intelligence Hub</h3>
            <span className="badge badge-cyan">MVP Audio Pipeline</span>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Speak naturally in Romanized Telugu, Telugu Script, or English (e.g., <em>"Customer aidhu vandalu ivvali vache vaaram"</em>)
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Dialect:</span>
          <span className="badge badge-neutral">Telugu Code-Mixed (TG/AP)</span>
        </div>
      </div>

      {/* Main Microphone & Waveform Action Center */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '24px 16px', background: 'rgba(0,0,0,0.3)', borderRadius: 'var(--radius-lg)', border: '1px dashed rgba(6, 182, 212, 0.25)', marginBottom: '20px' }}>
        
        {/* Animated Waveform Visualizer */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', height: '60px', marginBottom: '20px' }}>
          {waveformBars.map((height, idx) => (
            <div
              key={idx}
              className="waveform-bar"
              style={{
                height: `${isRecording ? height : 14}px`,
                background: isRecording
                  ? 'linear-gradient(to top, #06B6D4, #34D399)'
                  : 'rgba(255, 255, 255, 0.15)',
                transition: 'height 0.1s ease'
              }}
            />
          ))}
        </div>

        {/* Live Mic Button */}
        <button
          onClick={toggleRecording}
          disabled={isProcessing}
          className={`btn ${isRecording ? 'mic-active' : 'btn-primary'}`}
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            padding: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.4rem',
            marginBottom: '12px'
          }}
          title={isRecording ? "Click to stop listening" : "Click to speak"}
        >
          {isRecording ? <MicOff size={28} /> : <Mic size={28} />}
        </button>

        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: isRecording ? '#38BDF8' : 'var(--text-muted)' }}>
          {isRecording ? "Listening to Telugu / English speech..." : isProcessing ? "Parsing Spoken Numerals & NLP..." : "Tap to Speak or click a sample below"}
        </div>

        {liveTranscript && (
          <div style={{ marginTop: '12px', padding: '8px 16px', background: 'rgba(6, 182, 212, 0.15)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(6, 182, 212, 0.3)', fontSize: '0.9rem', color: 'var(--text-main)' }}>
            "{liveTranscript}"
          </div>
        )}
      </div>

      {/* 1-Click Realistic Spoken Audio Test Scenarios */}
      <div>
        <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
          1-Click Spoken Audio Scenarios (Instant Testing)
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
          {samplePrompts.map((sample) => (
            <button
              key={sample.id}
              onClick={() => handleExecuteAudio(sample.spoken_telugu)}
              disabled={isProcessing}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '10px 14px',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.5)';
                e.currentTarget.style.background = 'var(--bg-card-subtle)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
                e.currentTarget.style.background = 'var(--bg-card)';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38BDF8' }}>{sample.title}</span>
                <span className="badge badge-neutral" style={{ fontSize: '0.62rem' }}>{sample.badge}</span>
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#F8FAFC' }}>
                "{sample.spoken_telugu}"
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                {sample.english_meaning}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
