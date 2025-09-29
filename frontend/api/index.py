# Import the FastAPI app from main.py using relative import
from .main import app
import os
import sys

# Add diagnostic endpoints
@app.get("/__debug")
async def debug_info():
    return {
        "ok": True,
        "runtime": "vercel-python",
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "env_vars": {
            "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
            "INGEST_TOKEN": bool(os.getenv("INGEST_TOKEN")),
            "VERCEL": os.getenv("VERCEL", "not_set"),
            "VERCEL_ENV": os.getenv("VERCEL_ENV", "not_set")
        },
        "path": sys.path[:5]  # First 5 paths
    }

@app.get("/__whoami")
async def whoami():
    return {"ok": True, "runtime": "vercel-python", "app": "dronewatch"}