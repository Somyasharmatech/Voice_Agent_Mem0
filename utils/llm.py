import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
import requests
from utils.logger import get_logger

logger = get_logger(__name__)

def list_ollama_models() -> List[str]:
    """
    Fetches the list of available models from the local Ollama instance.
    """
    try:
        base_url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [model['name'] for model in response.json().get('models', [])]
            return models
        return []
    except Exception as e:
        logger.warning(f"Failed to fetch Ollama models: {str(e)}")
        return []

def generate_response(
    prompt: str, 
    system_prompt: str = "You are a helpful AI assistant.", 
    provider: str = "ollama", 
    api_key: Optional[str] = None, 
    model: str = "llama3", 
    response_format: Optional[str] = None
) -> str:
    """
    Generates a response using either OpenAI, Groq, or a local Ollama instance.
    Defaults to Ollama for privacy and local processing.
    """
    logger.info(f"Generating LLM response. Provider='{provider}', Model='{model}'")
    
    if provider.lower() in ["openai", "groq"]:
        if not api_key:
            logger.error(f"{provider} API key missing.")
            return f"Error: {provider} API key is missing."
        
        try:
            # Groq uses identical SDK as OpenAI, just a different base URL
            base_url = "https://api.groq.com/openai/v1" if provider.lower() == "groq" else None
            client = OpenAI(api_key=api_key, base_url=base_url)
            
            kwargs: Dict[str, Any] = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            response = client.chat.completions.create(**kwargs)
            logger.info(f"Successfully received {provider} response.")
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"{provider} completion failed: {str(e)}", exc_info=True)
            return f"{provider} Error: {str(e)}"
    
    elif provider.lower() == "ollama":
        base_url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
        url = f"{base_url}/api/generate"
        
        # When using JSON, instruct Ollama explicitly via format option
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\nUser: {prompt}",
            "stream": False
        }
        if response_format == "json":
            payload["format"] = "json"
            
        try:
            logger.debug(f"Sending request to Ollama URL: {url}")
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            logger.info("Successfully received Ollama response.")
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama network/request error: {str(e)}", exc_info=True)
            return f"Ollama Error: {str(e)}"
        except Exception as e:
            logger.error(f"Ollama unexpected error: {str(e)}", exc_info=True)
            return f"Ollama Error: {str(e)}"
    
    logger.error(f"Unknown LLM provider specified: {provider}")
    return "Error: Unknown provider."
