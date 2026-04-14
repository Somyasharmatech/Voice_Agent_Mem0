import os
import json
from openai import OpenAI
import requests

def generate_response(prompt, system_prompt="You are a helpful AI assistant.", provider="openai", api_key=None, model="gpt-4o", response_format=None):
    """
    Generates a response using either OpenAI or a local Ollama instance.
    """
    if provider.lower() == "openai":
        if not api_key:
            return "Error: OpenAI API key is missing."
        client = OpenAI(api_key=api_key)
        
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI Error: {str(e)}"
    
    elif provider.lower() == "ollama":
        url = "http://localhost:11434/api/generate"
        
        # When using JSON, instruct Ollama explicitly via format option
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\nUser: {prompt}",
            "stream": False
        }
        if response_format == "json":
            payload["format"] = "json"
            
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Ollama Error: {str(e)}"
    
    return "Error: Unknown provider."
