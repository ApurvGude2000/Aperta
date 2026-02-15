#!/bin/bash
# ABOUTME: Setup script for Fetch.ai agent environment.
# ABOUTME: Creates virtual environment and installs dependencies.

set -e

echo "🚀 Setting up Fetch.ai Agentverse Integration"
echo "=============================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Virtual environment created"
echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your credentials:"
    echo "   - FETCHAI_API_KEY"
    echo "   - AGENT_SEED (min 32 characters)"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

echo "=============================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your Fetch.ai credentials"
echo "  2. Start the FastAPI backend: cd ../backend && python main.py"
echo "  3. Start Fetch.ai agents: source venv/bin/activate && python main.py"
echo ""
echo "For testing: python test_agents.py"
echo "=============================================="
