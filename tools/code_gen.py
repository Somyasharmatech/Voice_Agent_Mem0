import subprocess
import os
from typing import Tuple, Optional
from utils.llm import generate_response
from tools.file_ops import create_file
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_code(
    prompt: str, 
    language: str, 
    provider: str = "openai", 
    api_key: Optional[str] = None, 
    model: str = "gpt-4o"
) -> str:
    """
    Generates code based on the prompt using the configured LLM.
    Returns the raw code string without markdown formatting.

    Args:
        prompt (str): The user's prompt or requirements.
        language (str): The programming language to generate.
        provider (str, optional): The LLM provider. Defaults to "openai".
        api_key (Optional[str], optional): The API key if needed. Defaults to None.
        model (str, optional): The model name. Defaults to "gpt-4o".

    Returns:
        str: Raw code content.
    """
    logger.info(f"Generating {language} code via {provider}...")
    
    system_prompt = (
        f"You are an expert {language} developer. Write the code requested by the user. "
        "Do not include any explanations, markdown formatting blocks (like ```python) around the code. "
        "Output ONLY the raw code."
    )
                    
    try:
        code_content = generate_response(prompt, system_prompt=system_prompt, provider=provider, api_key=api_key, model=model)
    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}", exc_info=True)
        return ""
        
    # Clean up markdown fences if LLM ignored instructions
    code_content = code_content.strip()
    if code_content.startswith("```"):
        first_newline = code_content.find("\n")
        if first_newline != -1:
            code_content = code_content[first_newline+1:]
    if code_content.endswith("```"):
        last_idx = code_content.rfind("```")
        if last_idx != -1:
            code_content = code_content[:last_idx]
            
    logger.info("Code generation successful.")
    return code_content.strip()

def run_python_code(filepath: str) -> Tuple[bool, str]:
    """
    Executes Python code safely using subprocess and returns the output.
    Checks for `ALLOW_CODE_EXECUTION` environment variable mapping.

    Args:
        filepath (str): Path to the Python file to execute.

    Returns:
        Tuple[bool, str]: (Success status boolean, Subprocess output or error message)
    """
    if os.getenv("ALLOW_CODE_EXECUTION", "false").lower() != "true":
        logger.warning(f"Code execution denied for security reasons. Target: {filepath}")
        return False, "Code execution is disabled for security reasons in this environment. Set ALLOW_CODE_EXECUTION=true to enable."

    if not filepath.endswith(".py"):
        logger.warning(f"Attempted to execute non-python file: {filepath}")
        return False, "Only Python files can be executed."
        
    if not os.path.exists(filepath):
        logger.error(f"Attempted to execute missing file: {filepath}")
        return False, "File does not exist."
        
    try:
        logger.info(f"Executing Python script: {filepath}")
        result = subprocess.run(
            ["python", filepath], 
            capture_output=True, 
            text=True, 
            timeout=10 # Prevent infinite loops
        )
        if result.returncode == 0:
            logger.info("Script execution succeeded.")
            return True, result.stdout
        else:
            logger.error(f"Script execution returned non-zero code. Error:\n{result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        logger.warning(f"Execution timed out for {filepath}")
        return False, "Execution timed out (10s limit)."
    except Exception as e:
        logger.error(f"Execution failed due to exception: {str(e)}", exc_info=True)
        return False, f"Execution failed: {str(e)}"
