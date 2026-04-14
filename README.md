# 🎙️ Voice-Controlled AI Agent

## 📌 Project Overview
The **Voice-Controlled AI Agent** is a Streamlit-based application that acts as a secure, local-first intelligence assistant. It listens to voice commands, transcribes them using Whisper, understands multiple intents simultaneously via LLMs (OpenAI or Ollama), and autonomously performs tasks such as generating code, executing Python scripts, summarizing text, and managing files. All outputs are safely generated within an isolated `output/` directory, and destructive actions require explicit human confirmation.

## 🏗️ Architecture
The system follows a modular architecture:
1. **Audio Input**: Takes voice recording from microphone or uploaded `.wav`/`.mp3` files via Streamlit UI.
2. **Speech-to-Text (STT)**: Processes audio using `openai-whisper` and converts it into text transcripts.
3. **Intent Detection Engine**: Uses a system prompt against an LLM (`utils.llm`) to determine the user's intent and extracts parameters into a JSON array, supporting multi-action pipelines.
4. **Tools Execution**:
    - `file_ops.py`: Safely creates files.
    - `code_gen.py`: Prompts the AI for code and saves it to a file. Can also execute Python files via subprocess.
    - `summarizer.py`: Text summarization capabilities.
    - `file_search.py`: Navigates the output directory.
5. **Memory System**: Saves all chats, tool executions, and state changes into `memory.json`.
6. **Text-To-Speech (TTS)**: Reads out completion confirmations using `gTTS`.

## 🛠️ Tech Stack
- **Frontend / Framework**: Streamlit
- **Transcription**: `openai-whisper`, `torch`
- **Language Models**: `openai` API, `ollama` for localized inference.
- **Text-to-Speech**: `gTTS`
- **Logic / Scripting**: Python 3.10+

## 🚀 Setup Steps
1. Clone the repository.
   ```bash
   git clone https://github.com/Somyasharmatech/Voice_Agent_Mem0.git
   cd Voice_Agent_Mem0
   ```
2. Create and activate a Virtual Environment (Recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Optional: If using Ollama, ensure Ollama is installed and running `llama3` or your preferred model locally (`ollama run llama3`).

## ▶️ How to Run
Start the Streamlit application using:
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.
Use the configuration sidebar to toggle between OpenAI and Ollama, and optionally add your API key.

## ⚠️ Limitations
- **Transcription Time**: Using local Whisper without a GPU can be slow. A fallback API integration strategy is outlined in `stt.py` if needed.
- **Execution Safety**: Execution of AI-generated Python code uses the `subprocess` module. It enforces a timeout but lacks containerized sandboxing (e.g., Docker). Never run generated code that interfaces with critical system features blindly.
- **Audio Recorders**: Browser-based microphone recording might require application deployment behind HTTPS to access microphone permissions seamlessly, depending on your browser.
