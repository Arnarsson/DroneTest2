# Import the FastAPI app from main.py using relative import
from .main import app

# Add a simple health check
@app.get("/__whoami")
async def whoami():
    return {"ok": True, "runtime": "vercel-python", "app": "dronewatch"}