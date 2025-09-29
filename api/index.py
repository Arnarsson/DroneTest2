# Import the full FastAPI app from api/main.py (the one with our fixes)
import sys
import os

# Add the api directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app from main.py in the same directory
from main import app

# Add a simple health check
@app.get("/__whoami")
async def whoami():
    return {"ok": True, "runtime": "vercel-python", "app": "dronewatch"}