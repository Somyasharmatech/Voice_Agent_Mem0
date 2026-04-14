from utils.llm import generate_response

def summarize_text(text, provider="openai", api_key=None, model="gpt-4o"):
    """
    Uses the LLM to summarize a block of text.
    """
    system_prompt = "You are a concise expert summarizer. Provide a short, structured summary of the user's text."
    
    summary = generate_response(
        prompt=f"Please summarize the following text:\n\n{text}",
        system_prompt=system_prompt,
        provider=provider,
        api_key=api_key,
        model=model
    )
    
    return summary
