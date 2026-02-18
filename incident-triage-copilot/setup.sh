#!/bin/bash

# Setup script for Incident Triage Copilot

echo "🚨 Setting up Incident Triage Copilot..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ollama
    else
        echo "Please install Ollama manually: https://ollama.ai"
        exit 1
    fi
else
    echo "✅ Ollama found"
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data/incidents
mkdir -p data/logs
mkdir -p data/runbooks
mkdir -p data/golden_cases

# Pull Ollama model
echo ""
echo "🤖 Pulling LLM model (this may take a few minutes)..."
ollama pull llama3.2

# Start Ollama server in background
echo ""
echo "🚀 Starting Ollama server..."
ollama serve &
sleep 3

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the copilot:"
echo "  1. source venv/bin/activate"
echo "  2. streamlit run app.py"
echo ""
echo "Or simply run: ./run.sh"
