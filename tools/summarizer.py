from typing import Optional
from utils.llm import generate_response
from utils.logger import get_logger

logger = get_logger(__name__)

def summarize_text(
    text: str, 
    provider: str = "openai", 
    api_key: Optional[str] = None, 
    model: str = "gpt-4o"
) -> str:
    """
    Uses the LLM to summarize a block of text.

    Args:
        text (str): The raw text to summarize.
        provider (str, optional): The LLM provider to use. Defaults to "openai".
        api_key (Optional[str], optional): The API key if required. Defaults to None.
        model (str, optional): The model name. Defaults to "gpt-4o".

    Returns:
        str: The generated text summary.
    """
    logger.info(f"Starting text summarization. length={len(text)} provider={provider}")
    system_prompt = "You are a concise expert summarizer. Provide a short, structured summary of the user's text."
    
    try:
        summary = generate_response(
            prompt=f"Please summarize the following text:\n\n{text}",
            system_prompt=system_prompt,
            provider=provider,
            api_key=api_key,
            model=model
        )
        logger.info("Summarization completed.")
        return summary
    except Exception as e:
        logger.error(f"Summarization error: {str(e)}", exc_info=True)
        return "An error occurred while trying to summarize the text."
