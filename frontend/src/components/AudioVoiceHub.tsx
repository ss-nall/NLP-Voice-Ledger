import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Cpu, Sparkles } from 'lucide-react';
import { api, SpokenTextResponse } from '../api/client';
import { useLanguage } from '../context/LanguageContext';
import { speakVernacularFeedback, playAudioCue, createVoiceActivityDetector, VoiceActivityDetector } from '../utils/audio';

interface AudioVoiceHubProps {
  onProcessResult: (result: SpokenTextResponse, transcript: string) => void;
  isProcessing: boolean;
}

type SpeechCode = 'en-IN' | 'te-IN' | 'ta-IN' | 'hi-IN' | 'kn-IN' | 'ml-IN' | 'ur-IN' | 'gu-IN';

export const AudioVoiceHub: React.FC<AudioVoiceHubProps> = ({ onProcessResult, isProcessing }) => {
  const { language, meta, t } = useLanguage();
  const [isRecording, setIsRecording] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState('');
  const [voiceLang, setVoiceLang] = useState<SpeechCode>(meta.speechCode);
  const [samplePrompts, setSamplePrompts] = useState<any[]>([]);
  const [waveformBars, setWaveformBars] = useState<number[]>(Array(32).fill(20));
  const [ttsEnabled, setTtsEnabled] = useState<boolean>(true);
  const recognitionRef = useRef<any>(null);
  const vadRef = useRef<VoiceActivityDetector | null>(null);

  // Sync speech language when global app language changes
  useEffect(() => {
    setVoiceLang(meta.speechCode);
  }, [language, meta.speechCode]);

  useEffect(() => {
    loadSamplePrompts();
  }, [language]);

  const loadSamplePrompts = async () => {
    // Dynamic multilingual sample prompts tailored to current language across 8 Indian Languages
    const samplePresets: Record<string, any[]> = {
      te: [
        { id: '1', title: 'కస్టమర్ చెల్లింపు', spoken: 'రమేష్ కి 1000 ఇచ్చేశాను', meaning: 'Paid 1000 to Ramesh', badge: 'ఖర్చు' },
        { id: '2', title: 'కస్టమర్ బాకీ', spoken: 'రమేష్ నుండి 2500 రావాలి', meaning: 'Receive 2500 from Ramesh', badge: 'రావాల్సినవి' },
        { id: '3', title: 'సప్లయర్ చెల్లింపు', spoken: 'పవన్ కి 15000 చెల్లించాను', meaning: 'Paid 15000 to Pawan', badge: 'సప్లయర్' },
        { id: '4', title: 'తక్షణ నగదు విక్రయం', spoken: 'సురేష్ 500 నగదు ఇచ్చాడు', meaning: 'Suresh gave 500 cash', badge: 'నగదు' }
      ],
      ta: [
        { id: '1', title: 'கடன் விற்பனை', spoken: 'செல்வத்துக்கு 2000 கொடுக்கனும்', meaning: 'Need to pay 2000 to Selvam', badge: 'செலவு' },
        { id: '2', title: 'வாடிக்கையாளர் பாக்கி', spoken: 'முருகனிடமிருந்து 3500 வர வேண்டும்', meaning: 'Receive 3500 from Murugan', badge: 'வரவு' },
        { id: '3', title: 'சப்ளையர் கணக்கு', spoken: 'கண்ணனுக்கு 8000 கொடுத்தேன்', meaning: 'Paid 8000 to Kannan', badge: 'சப்ளையர்' },
        { id: '4', title: 'ரொக்க வசூல்', spoken: 'குமார் 1200 ரொக்கமாக தந்தார்', meaning: 'Kumar paid 1200 cash', badge: 'ரொக்கம்' }
      ],
      hi: [
        { id: '1', title: 'ग्राहक भुगतान', spoken: 'रमेश ने 1000 दिए', meaning: 'Ramesh paid 1000', badge: 'वसूली' },
        { id: '2', title: 'ग्राहक से लेना है', spoken: 'राहुल से 2500 लेना है', meaning: 'Owed 2500 by Rahul', badge: 'प्राप्य' },
        { id: '3', title: 'सप्लायर को देना है', spoken: 'पवन को 15000 देना है', meaning: 'Pay 15000 to Pawan', badge: 'देय' },
        { id: '4', title: 'दुकान का खर्च', spoken: 'दुकान के लिए 800 का सामान खरीदा', meaning: 'Bought 800 shop items', badge: 'खर्च' }
      ],
      kn: [
        { id: '1', title: 'ಗ್ರಾಹಕರ ಪಾವತಿ', spoken: 'ರಮೇಶ್ 1000 ಕೊಟ್ಟರು', meaning: 'Ramesh paid 1000', badge: 'ಸ್ವೀಕೃತಿ' },
        { id: '2', title: 'ಗ್ರಾಹಕರ ಬಾಕಿ', spoken: 'ಸುರೇಶ್ ನಿಂದ 2500 ಬರಬೇಕು', meaning: 'Receive 2500 from Suresh', badge: 'ಬಾಕಿ' },
        { id: '3', title: 'ಸಪ್ಲೈಯರ್ ಪಾವತಿ', spoken: 'ಪ್ರಕಾಶ್ ಗೆ 5000 ಕೊಟ್ಟೆ', meaning: 'Paid 5000 to Prakash', badge: 'ಸಪ್ಲೈಯರ್' },
        { id: '4', title: 'ವ್ಯಾಪಾರ ಖರೀದಿ', spoken: 'ಆನಂದ್ ರಿಂದ 8000 ಸರಕು ತಗೊಂಡಿದ್ದೀನಿ', meaning: 'Stock 8000 from Anand', badge: 'ಖರೀದಿ' }
      ],
      ml: [
        { id: '1', title: 'ഉപഭോക്തൃ പേയ്‌മെന്റ്', spoken: 'രമേഷ് 1000 രൂപ തന്നു', meaning: 'Ramesh paid 1000', badge: 'വരവ്' },
        { id: '2', title: 'ഉപഭോക്തൃ ബാക്കി', spoken: 'സുരേഷിൽ നിന്ന് 2500 ലഭിക്കാനുണ്ട്', meaning: 'Receive 2500 from Suresh', badge: 'ലഭിക്കാനുള്ളത്' },
        { id: '3', title: 'വിതരണക്കാരന്റെ കുടിശ്ശിക', spoken: 'മോഹന് 5000 കൊടുത്തു', meaning: 'Paid 5000 to Mohan', badge: 'വിതരണക്കാരൻ' },
        { id: '4', title: 'ക്രെഡിറ്റ് വാങ്ങൽ', spoken: 'പ്രദീപിൽ നിന്ന് 8000 രൂപയ്ക്ക് സാധനങ്ങൾ വാങ്ങി', meaning: 'Stock 8000 from Pradeep', badge: 'വാങ്ങൽ' }
      ],
      ur: [
        { id: '1', title: 'گاہک کی ادائیگی', spoken: 'رمیش نے 1000 روپے دیے', meaning: 'Ramesh paid 1000', badge: 'وصولی' },
        { id: '2', title: 'گاہک کا بقایا', spoken: 'طارق سے 2500 لینے ہیں', meaning: 'Receive 2500 from Tariq', badge: 'بقایا' },
        { id: '3', title: 'سپلائر کی ادائیگی', spoken: 'عمران کو 5000 ادا کیا', meaning: 'Paid 5000 to Imran', badge: 'سپلائر' },
        { id: '4', title: 'خریداری کا حساب', spoken: 'اسلم سے 8000 کا مال خریدا', meaning: 'Bought 8000 stock from Aslam', badge: 'خرید' }
      ],
      gu: [
        { id: '1', title: 'ગ્રાહક ચૂકવણી', spoken: 'રમેશે 1000 આપ્યા', meaning: 'Ramesh paid 1000', badge: 'વસૂલી' },
        { id: '2', title: 'ગ્રાહક બાકી', spoken: 'સુરેશ પાસેથી 2500 લેવાના છે', meaning: 'Receive 2500 from Suresh', badge: 'લેવાના' },
        { id: '3', title: 'સપ્લાયર ચૂકવણી', spoken: 'ભાવેશને 5000 ચૂકવ્યા', meaning: 'Paid 5000 to Bhavesh', badge: 'સપ્લાયર' },
        { id: '4', title: 'માલની ખરીદી', spoken: 'જીગ્નેશ પાસેથી 8000 નો માલ ખરીદ્યો', meaning: 'Stock 8000 from Jignesh', badge: 'ખરીદી' }
      ],
      en: [
        { id: '1', title: 'Customer Payment Received', spoken: 'Received 1000 cash from Ramesh', meaning: 'Received 1000 cash from Ramesh', badge: 'Inflow' },
        { id: '2', title: 'Customer Receivable', spoken: 'Ramesh owes 2500 for goods', meaning: 'Ramesh owes 2500', badge: 'Receivable' },
        { id: '3', title: 'Supplier Obligation', spoken: 'Pay 15000 to Pawan next week', meaning: 'Pay 15000 to Pawan', badge: 'Payable' },
        { id: '4', title: 'Supplier Payment Made', spoken: 'Transferred 5000 to Chandu via UPI', meaning: 'Transferred 5000 to Chandu', badge: 'Outflow' }
      ]
    };

    setSamplePrompts(samplePresets[language] || samplePresets['en']);
  };

  const hasSubmittedAudioRef = useRef<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const interimIntervalRef = useRef<any>(null);
  const isInterimTranscribingRef = useRef<boolean>(false);
  const [activeEngine, setActiveEngine] = useState<'cloud' | 'offline' | null>(null);

  // Start / Stop Browser Speech Recognition with Offline Fallback & VAD Auto-Stop
  const toggleRecording = () => {
    if (isRecording) {
      if (activeEngine === 'offline') {
        stopOfflineRecording();
      } else {
        stopRecording();
      }
    } else {
      if (!navigator.onLine) {
        startOfflineRecording();
      } else {
        startRecording();
      }
    }
  };

  const startRecording = async () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      startOfflineRecording();
      return;
    }

    try {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch (e) {}
      }

      hasSubmittedAudioRef.current = false;
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = voiceLang;

      recognition.onstart = () => {
        playAudioCue('start');
        setIsRecording(true);
        setActiveEngine('cloud');
        setLiveTranscript('');
        animateWaveform();
      };

      recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript + ' ';
        }
        transcript = transcript.trim();
        setLiveTranscript(transcript);
      };

      recognition.onend = () => {
        if (vadRef.current) {
          vadRef.current.stop();
          vadRef.current = null;
        }
        setIsRecording(false);
        setActiveEngine(null);
        if (liveTranscript.trim() && !hasSubmittedAudioRef.current) {
          hasSubmittedAudioRef.current = true;
          handleExecuteAudio(liveTranscript);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition notice:", event.error);
        if (event.error === 'network') {
          setIsRecording(false);
          setActiveEngine(null);
          startOfflineRecording();
          return;
        }
        setIsRecording(false);
        setActiveEngine(null);
      };

      recognitionRef.current = recognition;
      recognition.start();

      // Enable VAD 1.2s Silence Detection
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaStreamRef.current = stream;
        vadRef.current = createVoiceActivityDetector(stream, () => {
          console.log("🎤 VAD: 1.2s silence detected, auto-stopping speech recognition...");
          stopRecording();
        }, 1200);
      } catch (err) {
        console.warn("VAD mic stream note:", err);
      }

    } catch (e) {
      console.error(e);
      startOfflineRecording();
    }
  };

  const stopRecording = () => {
    if (vadRef.current) {
      vadRef.current.stop();
      vadRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(t => t.stop());
      mediaStreamRef.current = null;
    }
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (e) {}
    }
    setIsRecording(false);
    setActiveEngine(null);
  };

  const startOfflineRecording = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Microphone access is not supported in this browser context.");
        return;
      }

      hasSubmittedAudioRef.current = false;
      audioChunksRef.current = [];
      setLiveTranscript('');
      setIsRecording(true);
      setActiveEngine('offline');
      animateWaveform();
      playAudioCue('start');

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // Start VAD Silence Auto-Stop (1.2s threshold)
      vadRef.current = createVoiceActivityDetector(stream, () => {
        console.log("🔒 VAD Offline: 1.2s silence detected, auto-stopping offline recorder...");
        stopOfflineRecording();
      }, 1200);

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
            const langPrefix = voiceLang.split('-')[0];
            const interimRes = await api.transcribeOfflineAudio(interimBlob, langPrefix, true);
            if (interimRes.text && interimRes.text.trim()) {
              setLiveTranscript(interimRes.text.trim());
            }
          } catch (e) {
            // Silently ignore interim chunk errors
          } finally {
            isInterimTranscribingRef.current = false;
          }
        }
      }, 1400);

      recorder.onstop = async () => {
        if (vadRef.current) {
          vadRef.current.stop();
          vadRef.current = null;
        }
        if (interimIntervalRef.current) {
          clearInterval(interimIntervalRef.current);
          interimIntervalRef.current = null;
        }

        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach(t => t.stop());
          mediaStreamRef.current = null;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        if (audioBlob.size < 500) {
          setIsRecording(false);
          setActiveEngine(null);
          return;
        }

        try {
          const langPrefix = voiceLang.split('-')[0];
          const res = await api.transcribeOfflineAudio(audioBlob, langPrefix, false);
          const transcribedText = res.text ? res.text.trim() : '';

          setIsRecording(false);
          setActiveEngine(null);
          if (transcribedText) {
            setLiveTranscript(transcribedText);
            handleExecuteAudio(transcribedText);
          } else {
            setLiveTranscript("ℹ️ No clear speech detected offline.");
          }
        } catch (err: any) {
          console.error("Offline STT error:", err);
          setIsRecording(false);
          setActiveEngine(null);
          setLiveTranscript(`⚠️ Offline error: ${err.message}`);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250);
    } catch (err: any) {
      console.error("Microphone capture error:", err);
      setIsRecording(false);
      setActiveEngine(null);
      alert("Microphone permission denied or device error.");
    }
  };

  const stopOfflineRecording = () => {
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
    setIsRecording(false);
    setActiveEngine(null);
  };

  // Waveform Bar Animation loop
  const animateWaveform = () => {
    if (!isRecording) return;
    const newBars = Array(32).fill(0).map(() => {
      const vol = vadRef.current ? vadRef.current.getVolumeLevel() : 0.3;
      return Math.floor(Math.random() * (vol * 50 + 25)) + 12;
    });
    setWaveformBars(newBars);
    requestAnimationFrame(animateWaveform);
  };

  const handleExecuteAudio = async (text: string) => {
    if (!text || !text.trim()) return;
    try {
      const result = await api.processSpokenText(text);
      playAudioCue('success');

      if (ttsEnabled && result.text_response) {
        speakVernacularFeedback(result.text_response, voiceLang);
      }

      onProcessResult(result, text);
    } catch (err: any) {
      playAudioCue('alert');
      alert("Error processing audio: " + err.message);
    }
  };

  return (
    <div className="fin-card" style={{ background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(16, 185, 129, 0.04))', border: '1px solid rgba(6, 182, 212, 0.3)', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h3 style={{ fontSize: '1.25rem', color: '#38BDF8', margin: 0 }}>{t('voicehub.title')}</h3>
            <span className="badge badge-cyan">{t('voicehub.badge')}</span>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            {t('voicehub.subtitle')}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {/* Audio Spoken TTS Feedback Toggle */}
          <button
            type="button"
            onClick={() => setTtsEnabled(!ttsEnabled)}
            style={{
              background: ttsEnabled ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.12)',
              border: ttsEnabled ? '1px solid #10B981' : '1px solid #EF4444',
              borderRadius: '12px',
              padding: '5px 10px',
              color: ttsEnabled ? '#34D399' : '#F87171',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
            title={ttsEnabled ? "Vernacular Voice Feedback: ON (Click to Mute)" : "Vernacular Voice Feedback: MUTED (Click to Enable)"}
          >
            {ttsEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
            <span>{ttsEnabled ? '🔊 Spoken Voice: ON' : '🔇 Voice: Muted'}</span>
          </button>

          {/* 8-Language Speech Selector */}
          <select
            value={voiceLang}
            onChange={(e) => setVoiceLang(e.target.value as any)}
            style={{
              background: 'var(--bg-card-subtle)',
              color: 'var(--cyan)',
              border: '1px solid var(--cyan)',
              borderRadius: '12px',
              padding: '4px 10px',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            <option value="en-IN">🇬🇧 English (en-IN)</option>
            <option value="te-IN">🇮🇳 తెలుగు Telugu (te-IN)</option>
            <option value="ta-IN">🇮🇳 தமிழ் Tamil (ta-IN)</option>
            <option value="hi-IN">🇮🇳 हिन्दी Hindi (hi-IN)</option>
            <option value="kn-IN">🇮🇳 ಕನ್ನಡ Kannada (kn-IN)</option>
            <option value="ml-IN">🇮🇳 മലയാളം Malayalam (ml-IN)</option>
            <option value="ur-IN">🇮🇳 اردو Urdu (ur-IN)</option>
            <option value="gu-IN">🇮🇳 ગુજરાતી Gujarati (gu-IN)</option>
          </select>
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
          title={isRecording ? t('voice.stop_recording') : t('voice.tap_to_speak')}
        >
          {isRecording ? <MicOff size={28} /> : <Mic size={28} />}
        </button>

        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: isRecording ? '#38BDF8' : 'var(--text-muted)' }}>
          {isRecording ? t('voicehub.listening') : isProcessing ? t('voicehub.processing') : t('voicehub.tap_speak')}
        </div>

        {isRecording && (
          <div style={{ fontSize: '0.72rem', color: '#10B981', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Sparkles size={13} /> Hands-free VAD Active (auto-stops on 1.2s silence)
          </div>
        )}

        {liveTranscript && (
          <div style={{ marginTop: '12px', padding: '8px 16px', background: 'rgba(6, 182, 212, 0.15)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(6, 182, 212, 0.3)', fontSize: '0.9rem', color: 'var(--text-main)' }}>
            "{liveTranscript}"
          </div>
        )}
      </div>

      {/* 1-Click Realistic Spoken Audio Test Scenarios */}
      <div>
        <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
          {t('voicehub.scenarios_title')}
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
          {samplePrompts.map((sample) => (
            <button
              key={sample.id}
              onClick={() => handleExecuteAudio(sample.spoken)}
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
                "{sample.spoken}"
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                {sample.meaning}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
