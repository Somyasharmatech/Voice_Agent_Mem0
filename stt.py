import whisper
import os

# Lazily load the model so it doesn't block startup
_whisper_model = None

def transcribe_audio(audio_path, use_api_fallback=False, api_client=None):
    """
    Transcribes audio using a local Whisper model.
    Offers basic implementation for an API fallback (e.g., OpenAI API) if local is too slow.
    """
    global _whisper_model
    
    if not os.path.exists(audio_path):
        return {"error": "Audio file not found."}
        
    if use_api_fallback and api_client:
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = api_client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return {"text": transcript.text}
        except Exception as e:
            return {"error": f"API Transcribe Error: {str(e)}"}
            
    # Local fallback
    if _whisper_model is None:
        try:
            # Using 'base' for faster loading. Can switch to 'tiny' for speed, or 'small' for accuracy
            _whisper_model = whisper.load_model("base")
        except Exception as e:
            return {"error": f"Error loading local Whisper model: {str(e)}"}
            
    try:
        result = _whisper_model.transcribe(audio_path)
        return {"text": result["text"]}
    except Exception as e:
        return {"error": f"Transcription Error: {str(e)}"}
