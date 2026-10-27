/**
 * Audio Utilities: Web Audio API VAD (Voice Activity Detection),
 * Vernacular Speech Synthesis (TTS), and Synthetic Chimes.
 */

// Native Voice Synthesis with multi-lingual locale fallback
export const speakVernacularFeedback = (text: string, speechCode: string = 'en-IN'): boolean => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return false;
  }

  try {
    window.speechSynthesis.cancel();
    // Clean markdown, markdown links, emojis for clean speech output
    const cleanText = text
      .replace(/\*+/g, '')
      .replace(/#+/g, '')
      .replace(/`+/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/[\u{1F300}-\u{1F9FF}]/gu, '')
      .replace(/[⚠️✅🗓️💰📅📊⚡📦📝🙏❌⚙️💡🛡️💬⚖️🎙️]/g, '')
      .trim();

    if (!cleanText) return false;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = speechCode;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    // Pick best matching available voice if available
    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      const match = voices.find(v => v.lang === speechCode || v.lang.startsWith(speechCode.split('-')[0]));
      if (match) utterance.voice = match;
    }

    window.speechSynthesis.speak(utterance);
    return true;
  } catch (err) {
    console.warn("SpeechSynthesis error:", err);
    return false;
  }
};

// Web Audio API Chime synthesizer
export const playAudioCue = (type: 'start' | 'success' | 'alert' | 'click' = 'success') => {
  if (typeof window === 'undefined') return;
  try {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = new AudioContextClass();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    const now = ctx.currentTime;
    if (type === 'start') {
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.12);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      osc.start(now);
      osc.stop(now + 0.12);
    } else if (type === 'success') {
      osc.frequency.setValueAtTime(523.25, now); // C5
      osc.frequency.setValueAtTime(659.25, now + 0.08); // E5
      osc.frequency.setValueAtTime(783.99, now + 0.16); // G5
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
      osc.start(now);
      osc.stop(now + 0.3);
    } else if (type === 'alert') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(300, now);
      osc.frequency.setValueAtTime(200, now + 0.1);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      osc.start(now);
      osc.stop(now + 0.25);
    }
  } catch (e) {
    // Ignore audio context errors if blocked by browser policy
  }
};

export interface VoiceActivityDetector {
  stop: () => void;
  getVolumeLevel: () => number;
}

/**
 * Creates real-time Voice Activity Detection (VAD) with 1.2s silence threshold.
 * Fires `onSilence` when user stops speaking after initial speech detection.
 */
export const createVoiceActivityDetector = (
  stream: MediaStream,
  onSilence: () => void,
  silenceThresholdMs: number = 1200,
  minVolumeThreshold: number = 0.02
): VoiceActivityDetector => {
  let audioContext: AudioContext | null = null;
  let isRunning = true;
  let speechDetected = false;
  let lastSpeechTimestamp = Date.now();
  let currentVolume = 0;
  let animFrameId: number | null = null;

  try {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    audioContext = new AudioContextClass();
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 512;
    analyser.smoothingTimeConstant = 0.2;
    source.connect(analyser);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const checkAudio = () => {
      if (!isRunning) return;

      analyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) {
        sum += dataArray[i];
      }
      const avg = sum / bufferLength;
      currentVolume = avg / 255; // Normalize 0 to 1

      const now = Date.now();
      if (currentVolume > minVolumeThreshold) {
        speechDetected = true;
        lastSpeechTimestamp = now;
      } else if (speechDetected && (now - lastSpeechTimestamp > silenceThresholdMs)) {
        // Silence detected after speech! Trigger auto-stop
        isRunning = false;
        onSilence();
        return;
      }

      animFrameId = requestAnimationFrame(checkAudio);
    };

    animFrameId = requestAnimationFrame(checkAudio);
  } catch (err) {
    console.warn("VAD AudioContext initialization error:", err);
  }

  return {
    stop: () => {
      isRunning = false;
      if (animFrameId) cancelAnimationFrame(animFrameId);
      if (audioContext && audioContext.state !== 'closed') {
        try { audioContext.close(); } catch (e) {}
      }
    },
    getVolumeLevel: () => currentVolume
  };
};
