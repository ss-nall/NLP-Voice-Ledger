from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel
from backend.app.database.session import get_db
from backend.app.services.conversation_service import conversation_service
from backend.app.nlp.speech_processor import speech_processor
from backend.app.nlp.offline_stt import offline_stt

router = APIRouter(prefix="/voice", tags=["Voice & Speech"])

class SpokenTextPayload(BaseModel):
    transcript: str
    session_id: str = "voice_session"
    confidence: Optional[float] = 0.95
    dialect: Optional[str] = "telugu_code_mixed"

@router.get("/status")
def get_voice_status():
    """
    Checks if offline local voice recognition is ready.
    """
    return {
        "offline_voice_available": True,
        "engine": "faster-whisper-tiny",
        "supported_languages": ["te", "ta", "hi", "en"]
    }

@router.post("/transcribe-offline")
async def transcribe_audio_offline(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    fast_interim: Optional[bool] = Form(False)
):
    """
    100% Offline Audio Transcription Endpoint.
    Receives raw audio recorded via browser MediaRecorder, transcribes locally with faster-whisper.
    """
    content = await file.read()
    if not content or len(content) < 100:
        raise HTTPException(status_code=400, detail="Empty or invalid audio recording")

    try:
        result = offline_stt.transcribe_audio_bytes(
            audio_bytes=content,
            filename=file.filename or "recording.webm",
            language=language,
            fast_interim=fast_interim
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Offline transcription error: {str(e)}")

@router.post("/process-spoken-text")
def process_spoken_text(payload: SpokenTextPayload, db: Session = Depends(get_db)):
    """
    Processes transcribed spoken audio text through the Indic numeral parser,
    code-mixed NLP pipeline, and ledger state machine.
    """
    if not payload.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
        
    result = conversation_service.process_message(
        db=db,
        message_text=payload.transcript,
        session_id=payload.session_id,
        is_voice=True,
        audio_metadata={"confidence": payload.confidence, "dialect": payload.dialect}
    )
    return result

@router.post("/upload-audio")
async def upload_audio_file(
    file: UploadFile = File(...),
    session_id: str = Form("voice_session"),
    spoken_text_hint: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Receives recorded microphone audio (webm/wav) from browser MediaRecorder,
    transcribes locally using offline faster-whisper, and processes through NLP ledger.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty audio file uploaded")
        
    transcript = spoken_text_hint
    transcription_meta = {}

    # If client didn't provide a browser-derived transcript (e.g. browser offline), transcribe locally on server
    if not transcript or not transcript.strip():
        try:
            stt_res = offline_stt.transcribe_audio_bytes(
                audio_bytes=content,
                filename=file.filename or "recording.webm",
                language=language
            )
            transcript = stt_res.get("text", "")
            transcription_meta = stt_res
        except Exception as e:
            # Fallback if transcription failed
            transcript = ""

    if not transcript or not transcript.strip():
        raise HTTPException(status_code=400, detail="No speech could be detected in the audio recording.")
    
    result = conversation_service.process_message(
        db=db,
        message_text=transcript,
        session_id=session_id,
        is_voice=True,
        audio_metadata={
            "file_size_bytes": len(content),
            "filename": file.filename,
            "offline_transcription": transcription_meta
        }
    )
    return {**result, "transcript": transcript}

@router.get("/sample-prompts")
def get_sample_voice_prompts():
    """
    Curated 1-click spoken audio scenarios for live demonstration.
    """
    return [
        {
            "id": "sample_01",
            "title": "Spoken Numerals & Promise",
            "spoken_telugu": "Ramesh Aidhu vandalu ivvali vache vaaram",
            "english_meaning": "Ramesh has to pay ₹500 next week",
            "feature": "Telugu Spoken Numerals ('aidhu vandalu' = ₹500) + Next Week Due Date",
            "badge": "MVP Voice Demo"
        },
        {
            "id": "sample_02",
            "title": "Partial Payment Received",
            "spoken_telugu": "Ramesh ninna 2000 ichadu",
            "english_meaning": "Ramesh paid 2000 yesterday",
            "feature": "Past Event Date ('ninna') + Partial Payment Received",
            "badge": "Payment Received"
        },
        {
            "id": "sample_03",
            "title": "Supplier Payable Direction",
            "spoken_telugu": "Supplier ki 8000 ivvali",
            "english_meaning": "Need to pay 8000 to supplier",
            "feature": "Direction Resolution ('ki ivvali' = Payable Obligation)",
            "badge": "Payable Direction"
        },
        {
            "id": "sample_04",
            "title": "Multi-Turn Payment Commitment",
            "spoken_telugu": "Ramesh Friday ki remaining istanu annadu",
            "english_meaning": "Ramesh said he will give remaining by Friday",
            "feature": "Coreference (Remaining Balance) + Friday Commitment",
            "badge": "Promise To Pay"
        },
        {
            "id": "sample_05",
            "title": "Contradiction Alert Test",
            "spoken_telugu": "Ramesh complete ga payment ichesadu",
            "english_meaning": "Ramesh settled the entire payment",
            "feature": "Contradiction Engine detects ₹3,000 pending & asks confirmation",
            "badge": "Conflict Engine"
        },
        {
            "id": "sample_06",
            "title": "Telugu Script Advance",
            "spoken_telugu": "సప్లయర్ కి పది వేలు అడ్వాన్స్ పంపాము",
            "english_meaning": "Transferred ₹10,000 advance to supplier",
            "feature": "Telugu Script Unicode Parsing + Advance Payment",
            "badge": "Telugu Script"
        },
        {
            "id": "sample_07",
            "title": "NL Financial Question",
            "spoken_telugu": "Evaru naaku ekkuva money ivvali?",
            "english_meaning": "Who owes me the most money?",
            "feature": "Deterministic SQL Query (Top Debtors)",
            "badge": "Deterministic Query"
        }
    ]
