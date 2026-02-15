#!/bin/bash

# Aperta Supabase Setup Script
# This script sets up Aperta with Supabase PostgreSQL database

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    Aperta Supabase Setup Script                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env not found!"
    echo "   Please ensure .env file is created with Supabase credentials"
    exit 1
fi

echo ""
echo "✅ Found .env file"

# Navigate to backend directory
cd backend

echo ""
echo "📦 Installing Python dependencies..."
echo "   This may take a few minutes..."

pip install -r requirements.txt > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🔗 Testing Supabase configuration..."

python3 << 'PYEOF'
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

try:
    from config import settings

    if settings.supabase_db_password and settings.supabase_url:
        print("✅ Supabase configuration found!")
        print(f"   URL: {settings.supabase_url}")
        print(f"   Database URL: {settings.database_url[:50]}...")
    else:
        print("⚠️  Supabase configuration incomplete")
        print("   Please check your .env file")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error loading configuration: {e}")
    sys.exit(1)

PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "🚀 Setup complete!"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "NEXT STEPS:"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "1. Set your Anthropic API key (required):"
echo "   export ANTHROPIC_API_KEY=\"your-api-key\""
echo ""
echo "2. Set your HuggingFace token (required for speaker diarization):"
echo "   export HF_TOKEN=\"hf_xxxxx\""
echo ""
echo "3. Start the backend server:"
echo "   python main.py"
echo ""
echo "4. The server will automatically:"
echo "   ✅ Connect to Supabase PostgreSQL"
echo "   ✅ Create all database tables"
echo "   ✅ Be ready for requests"
echo ""
echo "5. Upload audio to test:"
echo "   curl -X POST http://localhost:8000/audio/process \\"
echo "     -F \"file=@test_audio.wav\""
echo ""
echo "6. View your data in Supabase:"
echo "   https://supabase.com/dashboard"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
