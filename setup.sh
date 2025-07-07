#!/bin/bash

# Setup script for Text-to-SQL Agent

echo "Setting up Text-to-SQL Agent..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment template
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your actual credentials!"
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "⚠️  Ollama not found. Please install Ollama to use open-source models:"
    echo "   Visit: https://ollama.ai/download"
    echo "   Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
else
    echo "✅ Ollama is already installed"
    
    # Check if the default model is available
    if ! ollama list | grep -q "llama3.2:3b"; then
        echo "Downloading default model (llama3.2:3b)..."
        ollama pull llama3.2:3b
    else
        echo "✅ Default model (llama3.2:3b) is available"
    fi
fi

# Add testing at the end
echo ""
echo "Running system tests..."
python test_system.py

if [ $? -eq 0 ]; then
    echo "✅ Setup and testing complete!"
else
    echo "⚠️  Setup complete but some tests failed. Check configuration."
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Edit .env file with your AWS RDS credentials"
echo "3. Run: python database_setup.py (to create mock data)"
echo "4. Run: python text2sql_agent.py (for demo queries)"
echo "5. Run: python interactive_cli.py (for interactive mode)"
