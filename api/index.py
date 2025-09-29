from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create a simple FastAPI app directly here for testing
app = FastAPI(title="DroneWatch API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "DroneWatch API", "status": "working"}

@app.get("/api")
async def api_root():
    return {"message": "API endpoint", "status": "working"}

@app.get("/__whoami")
async def whoami():
    return {"ok": True, "runtime": "vercel-python", "app": "dronewatch"}