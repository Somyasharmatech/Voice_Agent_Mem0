import streamlit as st
import os
import time
import base64
from typing import Tuple, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from stt import transcribe_audio
from intent import detect_intents
from memory import save_memory, get_memory, clear_memory
from utils.llm import generate_response, list_ollama_models
from tools.file_ops import create_file, file_exists
from tools.code_gen import generate_code, run_python_code
from tools.summarizer import summarize_text
from tools.file_search import list_files, read_file
from utils.logger import get_logger
from gtts import gTTS

logger = get_logger(__name__)

# ---- PAGE CONFIGURATION ----
st.set_page_config(page_title="Voice AI Agent", page_icon="🎙️", layout="wide")

# ---- STYLING ----
def apply_styling():
    st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #c9d1d9; }
        .css-1y4p8pa { padding-top: 2rem; }
        .intent-box { background-color: #1f2937; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
        .success-box { background-color: #064e3b; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
        .error-box { background-color: #7f1d1d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ---- HELPER FUNCTIONS ----
def autoplay_audio(file_path: str):
    """Generates audio bytes and plays it automatically in the browser."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio controls autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error playing audio: {str(e)}")

def speak_text(text: str):
    """Creates a temporary MP3 file using gTTS and plays it."""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        autoplay_audio("response.mp3")
    except Exception as e:
        logger.error(f"TTS Error: {str(e)}")
        st.error(f"TTS Error: {e}")

# ---- UI COMPONENTS ----
def render_sidebar():
    """Renders the sidebar and returns configuration parameters."""
    with st.sidebar:
        st.header("⚙️ Agent Settings")
        
        # 1. LLM Provider
        # Default to Groq if we're on Hugging Face, otherwise Ollama
        is_cloud = os.getenv("SPACE_ID") is not None
        provider = st.radio("LLM Provider", ["Ollama (Local)", "Groq (API)"], index=1 if is_cloud else 0)
        provider_key = "ollama" if "Ollama" in provider else "groq"
        
        # 2. Model Selection
        if provider_key == "ollama":
            ollama_models = list_ollama_models()
            if ollama_models:
                model_choice = st.selectbox("Select local model", ollama_models, index=ollama_models.index("llama3:latest") if "llama3:latest" in ollama_models else 0)
            else:
                st.warning("⚠️ No local Ollama models found. Ensure Ollama is running.")
                model_choice = st.text_input("Enter Ollama Model Name manually:", value="llama3")
        else:
            api_choice = st.selectbox("Select API model", ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama-3.3-70b-versatile"])
            model_choice = api_choice
            
        # 3. STT Configuration
        st.markdown("---")
        st.subheader("🎙️ STT Settings")
        st.session_state.whisper_model = st.selectbox("Whisper Size", ["tiny", "base", "small"], index=1)
        st.session_state.use_stt_proxy = st.toggle("Use API for transcription fallback", value=True)
        
        st.markdown("---")
        st.subheader("🛠️ output/ Directory")
        if st.button("Refresh Files"):
            pass
        files = list_files()
        if files:
            for f in files:
                st.text(f"📄 {f}")
        else:
            st.caption("No files generated yet.")
            
        st.markdown("---")
        if st.button("Clear Memory"):
            clear_memory()
            st.success("Memory cleared!")
            
    return provider_key, os.getenv("GROQ_API_KEY", ""), model_choice

def process_intents(provider: str, api_key: str, model_choice: str):
    """Handles the execution pipeline for detected intents."""
    st.subheader("⚡ Actions & Results")
    combined_response = []
    
    for idx, intent in enumerate(st.session_state.intents):
        action_type = intent.get("intent")
        
        if action_type == "general_chat":
            msg = intent.get("message", "I didn't quite catch the message details.")
            st.markdown(f"<div class='success-box'>💬 AI: {msg}</div>", unsafe_allow_html=True)
            combined_response.append(msg)
            save_memory({"type": "chat", "user": st.session_state.transcription, "ai": msg})
            
        elif action_type == "summarize_text":
            topic = intent.get("text", intent.get("topic", "the transcription"))
            with st.spinner("Generating summary..."):
                summary = summarize_text(topic, provider=provider, api_key=api_key, model=model_choice)
                st.markdown(f"<div class='success-box'>📝 <b>Summary:</b><br/>{summary}</div>", unsafe_allow_html=True)
                combined_response.append("I have summarized the text.")
                save_memory({"type": "summarize", "topic": topic, "summary": summary})
                
        elif action_type == "search_file":
            fname = intent.get("file_name", intent.get("query", ""))
            if not fname:
                filenames = list_files()
                st.markdown(f"<div class='success-box'>📁 <b>Files found:</b> {', '.join(filenames)}</div>", unsafe_allow_html=True)
                combined_response.append(f"I found {len(filenames)} files.")
            else:
                content, status = read_file(fname)
                if content:
                    st.markdown(f"<div class='success-box'>📄 <b>Contents of {fname}:</b><br/><pre>{content[:500]}...</pre></div>", unsafe_allow_html=True)
                    combined_response.append(f"I read the file {fname}.")
                else:
                    st.error(status)
                    
        elif action_type in ["create_file", "write_code"]:
            fname = intent.get("file_name", "generated_snippet.py")
            action_key = f"action_{idx}_{fname}"
            
            if action_key not in st.session_state:
                st.session_state[action_key] = {"completed": False, "success": False, "msg": "", "fpath": "", "code": "", "lang": ""}

            if not st.session_state[action_key]["completed"]:
                st.warning(f"⚠️ Action Required: Wants to {action_type} for `{fname}`")
                if st.button(f"Confirm {action_type} for {fname}", key=f"confirm_{idx}"):
                    with st.spinner(f"Executing {action_type}..."):
                        if action_type == "create_file":
                            success, msg_out, fpath = create_file(fname, force_overwrite=True)
                            st.session_state[action_key] = {"completed": True, "success": success, "msg": msg_out, "fpath": fpath, "code": "", "lang": ""}
                        elif action_type == "write_code":
                            lang = intent.get("language", "python")
                            prompt = intent.get("prompt", st.session_state.transcription)
                            code = generate_code(prompt, lang, provider=provider, api_key=api_key, model=model_choice)
                            success, msg_out, fpath = create_file(fname, content=code, force_overwrite=True)
                            st.session_state[action_key] = {"completed": True, "success": success, "msg": msg_out, "fpath": fpath, "code": code, "lang": lang}
                    # Use st.rerun() if available, otherwise beta_rerun
                    if hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_rerun()
                        
            if st.session_state[action_key]["completed"]:
                res = st.session_state[action_key]
                if res["success"]:
                    st.success(res["msg"])
                    combined_response.append(f"I processed the file {fname}.")
                    if res["code"]:
                        with st.expander("Show Code"):
                            st.code(res["code"], language=res["lang"])
                        if res["lang"].lower() == "python":
                            st.info("Python code detected. You can run it below.")
                            if st.button(f"Run {fname}", key=f"run_{idx}"):
                                run_status, run_out = run_python_code(res["fpath"])
                                if run_status:
                                    st.markdown(f"**Output:**\n```\n{run_out}\n```")
                                else:
                                    st.error(f"Execution Error:\n{run_out}")
                else:
                    st.error(res["msg"])
                            
        elif action_type == "error":
            st.error(intent.get("message", "Unknown error parsing intent."))
            
    if combined_response:
        final_speech = " ".join(combined_response)
        if st.button("🔊 Play Initial Response"):
            speak_text(final_speech)

def main():
    apply_styling()
    st.title("🎙️ Voice-Controlled AI Agent")
    
    # Initialize State
    for key in ["current_audio", "transcription", "intents", "pending_actions"]:
        if key not in st.session_state:
            st.session_state[key] = None if key != "pending_actions" else []
            
    provider, api_key, model_choice = render_sidebar()
    
    tab1, tab2, tab3 = st.tabs(["🎤 Live Agent", "🔍 Output Explorer", "🧠 Memory History"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("1. Audio Input")
            audio_value = st.audio_input("Record a voice command") if hasattr(st, "audio_input") else None
            if not audio_value and not hasattr(st, "audio_input"):
                st.warning("Your Streamlit version doesn't support audio_input. Falling back to file uploader.")
                
            uploaded_file = st.file_uploader("Or upload an audio or video file", type=['wav', 'mp3', 'm4a', 'mp4'])
            final_audio = audio_value or uploaded_file
            
            if final_audio and final_audio != st.session_state.current_audio:
                st.session_state.current_audio = final_audio
                st.session_state.transcription = None
                st.session_state.intents = None
                st.session_state.pending_actions = []
                
                # Extract correct extension to prevent FFmpeg crashes
                ext = ".wav"
                if hasattr(final_audio, "name"):
                    ext = os.path.splitext(final_audio.name)[1]
                
                temp_filename = f"temp_audio{ext}"
                with open(temp_filename, "wb") as f:
                    f.write(final_audio.getbuffer())
                    
                with st.spinner(f"🎧 Transcribing with Whisper {st.session_state.whisper_model}..."):
                    # Use local Whisper with optional API fallback
                    transcript_res = transcribe_audio(
                        temp_filename, 
                        model_size=st.session_state.whisper_model,
                        use_api_fallback=st.session_state.use_stt_proxy,
                        # We pass a simple wrapper or just the API key if the stt utility can handle it
                    )
                    
                    if "error" in transcript_res:
                        st.error(transcript_res["error"])
                    else:
                        st.session_state.transcription = transcript_res["text"]
                        
                if st.session_state.transcription:
                    st.success("Transcription Complete.")
                    with st.spinner(f"🤖 Detecting Intent using {model_choice}..."):
                        st.session_state.intents = detect_intents(
                            st.session_state.transcription, 
                            provider=provider, 
                            api_key=api_key, 
                            model=model_choice
                        )
        with col2:
            st.subheader("2. Processing Pipeline")
            if st.session_state.transcription:
                st.markdown("**📝 Transcribed Text:**")
                st.info(st.session_state.transcription)
                
            if st.session_state.intents is not None:
                st.markdown("**🎯 Detected Intents:**")
                if len(st.session_state.intents) == 0:
                    st.info("No actionable intents were detected for this voice command! (The AI chose not to respond)")
                else:
                    for idx, intent in enumerate(st.session_state.intents):
                        i_type = intent.get('intent', 'unknown').replace('_', ' ').title()
                        details_html = "".join([f"<li><b>{k.replace('_', ' ').title()}</b>: {v}</li>" for k, v in intent.items() if k != 'intent'])
                        st.markdown(f"<div class='intent-box'><b>Intent {idx+1}:</b> {i_type} <ul style='margin-bottom:0px;'>{details_html}</ul></div>", unsafe_allow_html=True)
                    st.markdown("---")
                    process_intents(provider, api_key, model_choice)

    with tab2:
        st.subheader("🔍 Output Directory Explorer")
        out_files = list_files()
        if not out_files:
            st.info("No files generated yet.")
        else:
            selected_file = st.selectbox("Select a file to view", out_files)
            if selected_file:
                content, status = read_file(selected_file)
                if content is not None:
                    st.code(content)
                else:
                    st.error(status)
                    
    with tab3:
        st.subheader("🧠 System Memory")
        history = get_memory()
        if not history:
            st.info("Memory is empty.")
        else:
            for item in reversed(history):
                st.json(item)

if __name__ == "__main__":
    main()
