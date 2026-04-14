# Voice-Controlled AI Agent - 2-Minute Demo Script

## 0:00 - 0:20 | Introduction
*(Screen recording of the Streamlit application homepage. The user moves the mouse toward the sidebar to show configuration options.)*

**Voiceover:** "Hello everyone! Today, I want to show you my new Voice-Controlled AI Agent. This system acts as a secure, local companion that takes voice commands, transcribes them, and performs multi-step tool executions—like writing code, creating files, and summarization. It supports both local inferencing with Ollama and cloud AI with OpenAI."

## 0:20 - 0:45 | Audio Input & Transcription
*(User clicks on the "Live Agent" tab. They click the audio input button and record a phrase: "Create a python file called analysis.py and write a script to plot a simple graph. Also summarize the purpose of this project.")*

**Voiceover:** "Let's give it a test. I'm recording a complex, multi-intent prompt using my microphone directly in the browser. Watch as the system uses Whisper to quickly transcribe what I've said."

*(The screen shows "🎧 Transcribing audio..." followed by the text output.)*

## 0:45 - 1:15 | Multi-Intent Detection & Summarization
*(The UI displays "🎯 Detected Intents", showing three tasks: file creation, code generation, and text summarization. The successful text summary appears in a green box.)*

**Voiceover:** "Our Intent Engine has detected exactly what we want. Notice how it separated the tasks! First, it immediately generated a text summary because that's a non-destructive action. But for creating and modifying files, the system enforces a human-in-the-loop safety measure."

## 1:15 - 1:40 | Code Generation & Execution
*(User clicks 'Confirm create_file' and then 'Confirm write_code' on the UI warnings.)*

**Voiceover:** "To generate the file, I simply click these confirm buttons. The agent interfaces with the LLM to write a Python script for plotting a graph. It securely saves it directly to the 'output/' directory."

*(User expands the 'Show Code' dropdown to reveal the clean Python code. They then click the 'Run analysis.py' button, and the terminal output appears on the screen.)*

**Voiceover:** "Because it is a generated Python file, I can optionally choose to run it right here on the interface to test the output."

## 1:40 - 2:00 | System Memory & Output Navigation
*(User clicks the 'Output Explorer' tab to show the file, then navigates to the 'Memory History' tab. The agent's audio TTS system is triggered by clicking 'Play Initial Response'.)*

**Voiceover:** "Every interaction, including my past requests and file manipulations, is stored in persistent memory. And that's our Voice AI Agent! Fully open-source, modular, and ready for your complex workflows. Thanks for watching."
