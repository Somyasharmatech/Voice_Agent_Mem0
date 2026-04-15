import streamlit as st
import os
import time
from gtts import gTTS
import base64

from stt import transcribe_audio
from intent import detect_intents
from memory import save_memory, get_memory, clear_memory
from utils.llm import generate_response
from tools.file_ops import create_file, file_exists
from tools.code_gen import generate_code, run_python_code
from tools.summarizer import summarize_text
from tools.file_search import list_files, read_file

# ---- PAGE CONFIGURATION ----
st.set_page_config(page_title="Voice AI Agent", page_icon="🎙️", layout="wide")

# ---- STYLING ----
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .css-1y4p8pa { padding-top: 2rem; }
    .intent-box { background-color: #1f2937; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .success-box { background-color: #064e3b; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .error-box { background-color: #7f1d1d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ Voice-Controlled AI Agent")

# ---- SIDEBAR CONFIGURATION ----
with st.sidebar:
    st.header("⚙️ Configuration")
    provider = st.selectbox("LLM Provider", ["OpenAI", "Ollama"])
    api_key = None
    model_choice = "gpt-4o"
    
    if provider == "OpenAI":
        api_key = st.text_input("OpenAI API Key", type="password")
        model_choice = st.selectbox("Model", ["gpt-4o", "gpt-3.5-turbo", "gpt-4o-mini"])
    else:
        model_choice = st.text_input("Local Model Name", value="llama3")
        ollama_url = st.text_input("Ollama Endpoint URL", value=os.getenv("OLLAMA_URL", "http://localhost:11434"))
        os.environ["OLLAMA_URL"] = ollama_url
        
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

# ---- HELPER FUNCTIONS ----
def autoplay_audio(file_path: str):
    """Generates audio bytes and plays it automatically in the browser."""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

def speak_text(text):
    """Creates a temporary MP3 file using gTTS and plays it."""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        autoplay_audio("response.mp3")
    except Exception as e:
        st.error(f"TTS Error: {e}")

# ---- STATE MANAGEMENT ----
if "current_audio" not in st.session_state:
    st.session_state.current_audio = None
if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "intents" not in st.session_state:
    st.session_state.intents = None
if "pending_actions" not in st.session_state:
    st.session_state.pending_actions = []

# ---- TABS ----
tab1, tab2, tab3 = st.tabs(["🎤 Live Agent", "🔍 Output Explorer", "🧠 Memory History"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Audio Input")
        
        # Audio Input natively available in newer Streamlit versions
        if hasattr(st, "audio_input"):
            audio_value = st.audio_input("Record a voice command")
        else:
            st.warning("Your Streamlit version doesn't support audio_input. Falling back to file uploader.")
            audio_value = None
            
        uploaded_file = st.file_uploader("Or upload an audio file", type=['wav', 'mp3', 'm4a'])
        
        final_audio = audio_value or uploaded_file
        
        if final_audio and final_audio != st.session_state.current_audio:
            st.session_state.current_audio = final_audio
            st.session_state.transcription = None
            st.session_state.intents = None
            st.session_state.pending_actions = []
            
            # Save audio temporarily for Whisper
            with open("temp_audio.wav", "wb") as f:
                f.write(final_audio.getbuffer())
                
            with st.spinner("🎧 Transcribing audio..."):
                transcript_res = transcribe_audio("temp_audio.wav")
                if "error" in transcript_res:
                    st.error(transcript_res["error"])
                else:
                    st.session_state.transcription = transcript_res["text"]
                    
            if st.session_state.transcription:
                st.success("Transcription Complete.")
                with st.spinner("🤖 Detecting Intent..."):
                    if provider == "OpenAI" and not api_key:
                        st.error("Please provide an OpenAI API Key in the sidebar.")
                    else:
                        intents = detect_intents(
                            st.session_state.transcription, 
                            provider=provider, 
                            api_key=api_key, 
                            model=model_choice
                        )
                        st.session_state.intents = intents
                        # Prepare actions for human confirmation
                        st.session_state.pending_actions = [i for i in intents if i.get("intent") in ["create_file", "write_code"]]
                        
                        # Immediately execute non-destructive actions, or at least show them
                        
    with col2:
        st.subheader("2. Processing Pipeline")
        if st.session_state.transcription:
            st.markdown("**📝 Transcribed Text:**")
            st.info(st.session_state.transcription)
            
        if st.session_state.intents:
            st.markdown("**🎯 Detected Intents:**")
            for idx, intent in enumerate(st.session_state.intents):
                st.markdown(f"<div class='intent-box'><b>Intent {idx+1}:</b> {intent.get('intent')} <br/> <small>{intent}</small></div>", unsafe_allow_html=True)
                
            st.markdown("---")
            st.subheader("⚡ Actions & Results")
            
            # Non-destructive and confirmed actions logic
            combined_response = []
            
            for idx, intent in enumerate(st.session_state.intents):
                action_type = intent.get("intent")
                
                # --- GENERAL CHAT ---
                if action_type == "general_chat":
                    msg = intent.get("message", "I didn't quite catch the message details.")
                    st.markdown(f"<div class='success-box'>💬 AI: {msg}</div>", unsafe_allow_html=True)
                    combined_response.append(msg)
                    save_memory({"type": "chat", "user": st.session_state.transcription, "ai": msg})
                    
                # --- SUMMARIZE TEXT ---
                elif action_type == "summarize_text":
                    topic = intent.get("text", intent.get("topic", "the transcription"))
                    with st.spinner("Generating summary..."):
                        summary = summarize_text(topic, provider=provider, api_key=api_key, model=model_choice)
                        st.markdown(f"<div class='success-box'>📝 <b>Summary:</b><br/>{summary}</div>", unsafe_allow_html=True)
                        combined_response.append("I have summarized the text.")
                        save_memory({"type": "summarize", "topic": topic, "summary": summary})
                        
                # --- SEARCH FILE ---
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
                            
                # --- DESTRUCTIVE ACTIONS (CREATE / WRITE) : REQUIRE CONFIRMATION ---
                elif action_type in ["create_file", "write_code"]:
                    fname = intent.get("file_name", "generated_snippet.py")
                    
                    st.warning(f"⚠️ Action Required: Wants to {action_type} for `{fname}`")
                    
                    # Create a unique key for the button
                    confirm_key = f"confirm_{idx}"
                    
                    if st.button(f"Confirm {action_type} for {fname}", key=confirm_key):
                        with st.spinner(f"Executing {action_type}..."):
                            if action_type == "create_file":
                                success, msg_out, _ = create_file(fname, force_overwrite=True)
                                if success:
                                    st.success(f"File {fname} created!")
                                    combined_response.append(f"I created the file {fname}.")
                                    save_memory({"type": "create_file", "file": fname})
                                else:
                                    st.error(msg_out)
                                    
                            elif action_type == "write_code":
                                lang = intent.get("language", "python")
                                prompt = intent.get("prompt", st.session_state.transcription)
                                code = generate_code(prompt, lang, provider=provider, api_key=api_key, model=model_choice)
                                success, msg_out, fpath = create_file(fname, content=code, force_overwrite=True)
                                
                                if success:
                                    st.success(f"Code written to {fname}!")
                                    with st.expander("Show Code"):
                                        st.code(code, language=lang)
                                    combined_response.append(f"I wrote the code to {fname}.")
                                    save_memory({"type": "write_code", "file": fname, "language": lang})
                                    
                                    # Optional Python execution
                                    if lang.lower() == "python":
                                        st.info("Python code detected. You can run it below.")
                                        if st.button(f"Run {fname}", key=f"run_{idx}"):
                                            run_status, run_out = run_python_code(fpath)
                                            if run_status:
                                                st.markdown(f"**Output:**\n```\n{run_out}\n```")
                                            else:
                                                st.error(f"Execution Error:\n{run_out}")
                                else:
                                    st.error(msg_out)
                                    
                # Handle error intent
                elif action_type == "error":
                    st.error(intent.get("message", "Unknown error parsing intent."))
                    
            # TTS Output for non-destructive or completed actions
            if combined_response:
                final_speech = " ".join(combined_response)
                if st.button("🔊 Play Initial Response"):
                    speak_text(final_speech)

with tab2:
    st.subheader("🔍 Output Directory Explorer")
    out_files = list_files()
    if not out_files:
        st.info("No files generated yet. Use voice commands to create files or code.")
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
