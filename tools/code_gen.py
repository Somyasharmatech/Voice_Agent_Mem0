from utils.llm import generate_response
from tools.file_ops import create_file
import subprocess
import os

def generate_code(prompt, language, provider="openai", api_key=None, model="gpt-4o"):
    """
    Generates code based on the prompt using LLM.
    Returns the raw code string.
    """
    system_prompt = f"You are an expert {language} developer. Write the code requested by the user. " \
                    "Do not include any explanations, markdown formatting blocks (like ```python) around the code. " \
                    "Output ONLY the raw code."
                    
    code_content = generate_response(prompt, system_prompt=system_prompt, provider=provider, api_key=api_key, model=model)
    
    # Clean up markdown fences if LLM ignored instructions
    code_content = code_content.strip()
    if code_content.startswith("```"):
        # find the first newline to skip the ```python part
        first_newline = code_content.find("\n")
        if first_newline != -1:
            code_content = code_content[first_newline+1:]
    if code_content.endswith("```"):
        # remove last 3 chars
        last_idx = code_content.rfind("```")
        if last_idx != -1:
            code_content = code_content[:last_idx]
            
    return code_content.strip()

def run_python_code(filepath):
    """
    Executes Python code safely using subprocess and returns the output.
    """
    if os.getenv("ALLOW_CODE_EXECUTION", "false").lower() != "true":
        return False, "Code execution is disabled for security reasons in this environment. Set ALLOW_CODE_EXECUTION=true to enable."

    if not filepath.endswith(".py"):
        return False, "Only Python files can be executed."
        
    if not os.path.exists(filepath):
        return False, "File does not exist."
        
    try:
        result = subprocess.run(
            ["python", filepath], 
            capture_output=True, 
            text=True, 
            timeout=10 # Prevent infinite loops
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Execution timed out (10s limit)."
    except Exception as e:
        return False, f"Execution failed: {str(e)}"
