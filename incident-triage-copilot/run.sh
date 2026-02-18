#!/bin/bash

# Run script for Incident Triage Copilot

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🚀 Starting Ollama server..."
    ollama serve &
    sleep 3
fi

# Activate virtual environment
source venv/bin/activate

# Run Streamlit app
echo "🚨 Starting Incident Triage Copilot..."
streamlit run app.py
