"""
DroneWatch API - Vercel Entry Point
This file re-exports the FastAPI app for Vercel to detect
"""

# Import the FastAPI app from api/index.py
from api.index import app

# Add a simple health check at root
@app.get("/", include_in_schema=False)
def root():
    return {
        "name": "DroneWatch API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/api/docs",
        "endpoints": {
            "api": "/api",
            "healthz": "/api/healthz",
            "incidents": "/api/incidents"
        }
    }

# Vercel will automatically detect this 'app' variable