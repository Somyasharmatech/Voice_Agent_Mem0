import whisper
import os
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Lazily load the model so it doesn't block startup
_whisper_model = None

def transcribe_audio(audio_path: str, use_api_fallback: bool = False, api_client: Any = None) -> Dict[str, str]:
    """
    Transcribes audio using a local Whisper model.
    Offers basic implementation for an API fallback (e.g., OpenAI API) if local is too slow.

    Args:
        audio_path (str): The path to the audio file to transcribe.
        use_api_fallback (bool, optional): Whether to use an API fallback. Defaults to False.
        api_client (Any, optional): The OpenAI API client for fallback. Defaults to None.

    Returns:
        Dict[str, str]: A dictionary containing the "text" of transcription or an "error" message.
    """
    global _whisper_model
    
    logger.info(f"Attempting to transcribe audio file: {audio_path}")
    
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found at path: {audio_path}")
        return {"error": "Audio file not found."}
        
    if use_api_fallback and api_client:
        logger.info("Using API fallback for transcription.")
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = api_client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            logger.info("API Transcription successful.")
            return {"text": transcript.text}
        except Exception as e:
            logger.error(f"API Transcribe Error: {str(e)}", exc_info=True)
            return {"error": f"API Transcribe Error: {str(e)}"}
            
    # Local fallback
    if _whisper_model is None:
        logger.info("Loading local Whisper base model. This may take a moment...")
        try:
            # Using 'base' for faster loading. Can switch to 'tiny' for speed, or 'small' for accuracy
            _whisper_model = whisper.load_model("base")
            logger.info("Local Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading local Whisper model: {str(e)}", exc_info=True)
            return {"error": f"Error loading local Whisper model: {str(e)}"}
            
    try:
        logger.info("Starting local Whisper transcription...")
        result = _whisper_model.transcribe(audio_path)
        logger.info("Local Whisper transcription complete.")
        return {"text": result["text"]}
    except Exception as e:
        logger.error(f"Transcription Error: {str(e)}", exc_info=True)
        return {"error": f"Transcription Error: {str(e)}"}
