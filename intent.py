import json
from utils.llm import generate_response

def detect_intents(text, provider="openai", api_key=None, model="gpt-4o"):
    """
    Uses LLM to classify user intent from transcribed text into a JSON list.
    Supports multiple intents.
    """
    system_prompt = """
    You are an intent classification engine for an AI voice agent.
    Given the user's text, detect all the actions the user wants to perform.
    Support multiple intents if the user asks for more than one thing.
    
    Supported intents:
    - create_file: Requires 'file_name'.
    - write_code: Requires 'language', and 'prompt' (what code to write). Might also include 'file_name'.
    - summarize_text: Requires 'text' or 'topic' to summarize.
    - search_file: Requires 'query' or 'file_name'.
    - general_chat: Requires 'message' containing your conversational response.
    
    You MUST return ONLY a valid JSON list of dictionaries. Do not include markdown code blocks.
    
    Example input: "Create a python file called hello.py and write a hello world script in it."
    Example output JSON:
    [
      {"intent": "create_file", "file_name": "hello.py"},
      {"intent": "write_code", "language": "python", "prompt": "write a hello world script", "file_name": "hello.py"}
    ]
    """
    
    response_text = generate_response(
        prompt=text, 
        system_prompt=system_prompt, 
        provider=provider, 
        api_key=api_key, 
        model=model,
        response_format="json"
    )
    
    # Try cleaning markdown fences if the LLM leaked them
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
        
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
        
    try:
        intents = json.loads(clean_text)
        if not isinstance(intents, list):
            intents = [intents] # Wrap in list if a single dict was returned
        return intents
    except json.JSONDecodeError:
        return [{"intent": "error", "message": f"Failed to parse AI response into JSON. Raw response: {response_text}"}]
