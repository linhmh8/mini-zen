#!/bin/bash
# Start local AI Discussion Server

echo "🚀 Starting AI Discussion Server locally..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Set API keys from .env file if it exists
if [ -f ".env" ]; then
    echo "🔑 Loading API keys from .env file..."
    export $(cat .env | xargs)
else
    echo "⚠️  No .env file found. Copy .env.example to .env and add your API keys."
    echo "Using default keys for demo..."
    export OPENROUTER_API_KEY="your_openrouter_api_key_here"
    export GEMINI_API_KEY="your_gemini_api_key_here"
fi

# Start the server
echo "🌟 Starting server at http://localhost:8000"
echo "📖 API docs will be available at http://localhost:8000/docs"
echo "🔧 Health check at http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python local_server.py
