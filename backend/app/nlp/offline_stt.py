"""
100% Offline Speech-to-Text (STT) Engine using faster-whisper.
Runs entirely on local CPU with zero internet connection required.
Transcribes audio in Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, Gujarati, English, and 90+ languages.
"""

import os
import tempfile
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Compatibility patch for PyAV: some versions of `av.open` do not accept `metadata_errors`
try:
    import av
    _orig_av_open = av.open
    def _safe_av_open(*args, **kwargs):
        try:
            return _orig_av_open(*args, **kwargs)
        except TypeError as err:
            if "metadata_errors" in str(err):
                kwargs.pop("metadata_errors", None)
                return _orig_av_open(*args, **kwargs)
            raise err
    av.open = _safe_av_open
except Exception as _e:
    logger.debug(f"PyAV patch skipped: {_e}")

INDIC_DOMAIN_PROMPTS = {
    "te": "రమేష్, సురేష్, మహేష్, వెంకట్, చందు, పవన్, కుమార్, రాజు, కిరణ్, శ్రీను, భాస్కర్, 100, 500, 1000, 2000, 2500, 5000, 10000, ఐదు వందలు, రెండు వేలు, పది వేలు, ఇచ్చాను, ఇచ్చాడు, ఇవ్వాలి, రావాలి, బాకీ, ఖర్చు, ఖాతా, చెల్లించాను, వసూలు, aidhu vandalu, rendu vela, ichanu, ivvali, ravali, baki, cash, UPI, payment.",
    "ta": "செல்வம், முருகன், கார்த்திக், கண்ணன், குமார், விஜய், ராஜா, செந்தில், 100, 500, 1000, 2000, 2500, 5000, 10000, ஐநூறு, இரண்டாயிரம், பத்தாயிரம், கொடுத்தேன், கொடுத்தார், கொடுக்க வேண்டும், வர வேண்டும், பாக்கி, செலவு, ரொக்கம், kuduthen, koduthaar, kudukkanum, varanum, baki, cash, UPI, payment.",
    "hi": "रमेश, राहुल, अमित, सुरेश, पवन, विकास, रोहित, दीपक, 100, 500, 1000, 2000, 2500, 5000, 10000, पांच सौ, दो हजार, दस हजार, दिया, दिए, देना है, लेना है, जमा, हिसाब, उधार, नकद, diya, diye, dena hai, lena hai, jama, udhaar, cash, UPI, payment.",
    "kn": "ರಮೇಶ್, ಸುರೇಶ್, ಮಂಜುನಾಥ್, ಪ್ರಕಾಶ್, ಕಿರಣ್, ಆನಂದ್, ಕುಮಾರ್, 100, 500, 1000, 2000, 2500, 5000, 10000, ಐನೂರು, ಎರಡು ಸಾವಿರ, ಹತ್ತು ಸಾವಿರ, ಕೊಟ್ಟೆ, ಕೊಟ್ಟರು, ಕೊಡಬೇಕು, ಬರಬೇಕು, ಬಾಕಿ, ಖಾತೆ, ರೊಕ್ಕ, kotte, kottaru, kodabeku, barabeku, baki, cash, UPI, payment.",
    "ml": "രമേഷ്, സുരേഷ്, മോഹൻ, പ്രദീപ്, അനിൽ, വിജയൻ, രാഹുൽ, 100, 500, 1000, 2000, 2500, 5000, 10000, അഞ്ഞൂറ്, രണ്ടായിരം, പതിനായിരം, കൊടുത്തു, തന്നു, കൊടുക്കണം, തരണം, ബാക്കി, കണക്ക്, പണം, koduthu, thannu, kodukkanam, tharanam, baaki, cash, UPI, payment.",
    "ur": "رمیش, طارق, اسلم, عمران, فرحان, بلال, زبیر, 100, 500, 1000, 2000, 2500, 5000, 10000, پانچ سو, دو ہزار, دس ہزار, دیا, وصول ہوا, دینا ہے, لینا ہے, باقی, حساب, رقم, diya, wasool hua, dena hai, lena hai, baqi, cash, UPI, payment.",
    "gu": "રમેશ, સુરેશ, ભાવેશ, પરેશ, કિરણ, જીગ્નેશ, હિતેશ, 100, 500, 1000, 2000, 2500, 5000, 10000, પાંચસો, બે હજાર, દસ હજાર, આપ્યા, મળ્યા, આપવાના છે, લેવાના છે, બાકી, હિસાબ, રોકડ, aapya, malya, aapvana che, levana che, baki, cash, UPI, payment.",
    "en": "Ramesh, Suresh, Mahesh, Chandu, Kumar, Pawan, Deepak, 100, 500, 1000, 2500, 5000, 10000, five hundred, two thousand, ten thousand, paid, received, owes, due, balance, invoice, cash, UPI, payment, account."
}

def clean_stt_text(raw_text: str) -> str:
    """Cleans up common STT / Whisper hallucination artifacts."""
    if not raw_text:
        return ""
    
    tokens = raw_text.split()
    cleaned_tokens = []
    for t in tokens:
        if not cleaned_tokens or t.lower() != cleaned_tokens[-1].lower():
            cleaned_tokens.append(t)
            
    text = " ".join(cleaned_tokens).strip()
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^[,\.\-\s]+|[,\.\-\s]+$', '', text)
    return text

class OfflineSTTEngine:
    _instance = None
    _model = None

    def __init__(self, model_size: str = "tiny"):
        self.model_size = model_size

    @classmethod
    def get_instance(cls, model_size: str = "tiny"):
        if cls._instance is None:
            cls._instance = OfflineSTTEngine(model_size=model_size)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(f"Initializing local faster-whisper model ({self.model_size}) on CPU...")
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                logger.info(f"Loaded local faster-whisper model ({self.model_size}) successfully.")
            except Exception as e:
                logger.error(f"Error initializing faster-whisper: {e}")
                raise e
        return self._model

    def is_available(self) -> bool:
        try:
            import faster_whisper
            return True
        except ImportError:
            return False

    def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        language: Optional[str] = None,
        fast_interim: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribes raw audio bytes locally on device.
        Accepts formats like webm, wav, mp3, ogg across 8 languages.
        """
        ext = os.path.splitext(filename)[1] or ".webm"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            model = self._load_model()
            lang_map = {
                "te": "te",
                "ta": "ta",
                "hi": "hi",
                "kn": "kn",
                "ml": "ml",
                "ur": "ur",
                "gu": "gu",
                "en": "en"
            }
            target_lang = lang_map.get(language) if language else None
            beam = 1 if fast_interim else 3
            initial_prompt = INDIC_DOMAIN_PROMPTS.get(target_lang or "en", INDIC_DOMAIN_PROMPTS["en"])

            segments, info = model.transcribe(
                tmp_path,
                beam_size=beam,
                language=target_lang,
                initial_prompt=initial_prompt,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=350, speech_pad_ms=250),
                condition_on_previous_text=False,
                temperature=0.0
            )
            
            text_segments = [s.text.strip() for s in segments]
            raw_full_text = " ".join(text_segments).strip()
            cleaned_text = clean_stt_text(raw_full_text)

            return {
                "text": cleaned_text,
                "detected_language": info.language,
                "language_probability": round(info.language_probability, 3) if info.language_probability else 1.0,
                "duration": round(info.duration, 2) if info.duration else 0.0,
                "offline": True
            }
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

offline_stt = OfflineSTTEngine.get_instance("tiny")
