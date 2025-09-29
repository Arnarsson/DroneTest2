# For Vercel, we need to export the FastAPI app directly
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

# Vercel expects a handler variable for Python functions
handler = app