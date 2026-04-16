import whisper
import os
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Lazily load the model so it doesn't block startup
_whisper_model = None
_current_model_size = None

def transcribe_audio(
    audio_path: str, 
    model_size: str = "base", 
    use_api_fallback: bool = False, 
    api_client: Any = None
) -> Dict[str, str]:
    """
    Transcribes audio using a local Whisper model or an API fallback.

    Args:
        audio_path (str): The path to the audio file.
        model_size (str): The Whisper model size ('tiny', 'base', 'small', etc.).
        use_api_fallback (bool): Whether to use API if local fails.
        api_client (Any): OpenAI client for API fallback.
    """
    global _whisper_model
    global _current_model_size
    
    logger.info(f"Transcribing {audio_path} using model='{model_size}' (API fallback: {use_api_fallback})")
    
    if not os.path.exists(audio_path):
        return {"error": "Audio file not found."}

    # Handle local transcription
    try:
        # Check if we need to load or reload the model
        if _whisper_model is None or _current_model_size != model_size:
            logger.info(f"Loading local Whisper {model_size} model...")
            _whisper_model = whisper.load_model(model_size)
            _current_model_size = model_size

        result = _whisper_model.transcribe(audio_path)
        return {"text": result["text"]}
    except Exception as e:
        logger.error(f"Local Transcription failed: {str(e)}")
        if use_api_fallback and api_client:
            logger.info("Switching to API fallback...")
            try:
                with open(audio_path, "rb") as f:
                    transcript = api_client.audio.transcriptions.create(model="whisper-1", file=f)
                return {"text": transcript.text}
            except Exception as api_e:
                return {"error": f"Both local and API transcription failed. API Error: {str(api_e)}"}
        return {"error": f"Transcription Error: {str(e)}"}
