# api/index.py
# Re-export the FastAPI app for Vercel
from .main import app  # Import from api/main.py using relative import

# Add a quick ping endpoint for testing
@app.get("/__whoami", include_in_schema=False)
def whoami():
    return {"ok": True, "runtime": "vercel-python", "app": "dronewatch"}

# IMPORTANT: Export 'app' not 'handler' for FastAPI on Vercel