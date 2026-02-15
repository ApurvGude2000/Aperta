"""
Vercel serverless entry point for Aperta backend.
"""
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app

# Export app for Vercel
handler = app
