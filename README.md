---
title: Voice AI Agent
emoji: 🎙️
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
---

# 🎙️ Local Voice-Controlled AI Agent

A robust, local-first AI assistant built with **Streamlit**, **Ollama**, and **OpenAI Whisper**. This agent allows you to control your local machine using voice commands, performing tasks like file creation, code generation, and text summarization with extreme privacy and zero-latency (when running locally).

## 🚀 Key Features
- **Local Transcription:** Uses OpenAI Whisper (Tiny/Base/Small) to convert speech to text on your hardware.
- **Intent Understanding:** Leverages **Ollama** (Llama 3/Mistral) to classify user intents and extract parameters.
- **Dynamic Tool Execution:**
  - 📁 **File Operations:** Create and manage files/folders in a secure `/output` directory.
  - 💻 **Code Generation:** Generate and execute Python snippets locally.
  - 📝 **Summarization:** Condense long transcriptions into concise summaries.
- **Hardware Workarounds:** If local processing (Ollama/Whisper) is too slow or inefficient on your machine, the system includes an API-based fallback (Groq/OpenAI) as permitted by the assignment guidelines.
- **Clean UI:** Simple, dark-mode Streamlit interface displaying transcriptions, intents, actions, and outputs.

## 🏗️ Architecture
The system follows a modular pipeline:
1. **Audio Input:** Captured via `st.audio_input` (Microphone) or File Upload.
2. **STT (Speech-to-Text):** Local Whisper model processes the audio.
3. **Intent Detection:** The transcription is sent to a local LLM (via Ollama) which returns structured JSON intents.
4. **Tool Triggering:** Specific Python scripts are executed based on the detected intent (File Ops, Code Gen, etc.).
5. **Output:** Results are displayed in the UI and stored in the `output/` folder.

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com/) installed and running.
- [FFmpeg](https://ffmpeg.org/) (required for audio processing).

### Installation
1. **Clone the repository:**
   ```bash
   git clone <your-repo-link>
   cd local-voice-agent
   ```
2. **Setup virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Configuration:**
   Create a `.env` file:
   ```env
   GROQ_API_KEY=your_key_here  # Optional fallback
   OLLAMA_URL=http://localhost:11434
   ```

### Running the Agent
1. Start Ollama: `ollama run llama3`
2. Launch the UI:
   ```bash
   streamlit run app.py
   ```

## 🛡️ Safety & Security
- **Isolated Workspace:** All file/folder operations are restricted to the `output/` directory.
- **Human-in-the-Loop:** Destructive or file-writing actions require manual confirmation in the UI.

## 📝 Assignment Deliverables
- **Technical Article:** Located in [tech_article.md](tech_article.md).
- **Video Script:** Located in [video_script.md](video_script.md).

---
*Created for the "Voice-Controlled Local AI Agent" Project Assignment.*
