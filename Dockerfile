FROM python:3.10-slim

WORKDIR /app

# Install ffmpeg for whisper audio processing
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Prevent code execution by default in cloud
ENV ALLOW_CODE_EXECUTION=false
# Avoid Streamlit usage stats
ENV STREAMLIT_SERVER_GATHER_USAGE_STATS=false

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
