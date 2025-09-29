# Import the FastAPI app from main.py
from .main import app

# Export handler for Vercel
handler = app