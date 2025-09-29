from datetime import datetime

def handler(request, response):
    """Simple test endpoint for Vercel"""
    response.status_code = 200
    return {
        "message": "Python API is working!",
        "timestamp": datetime.now().isoformat(),
        "path": request.url
    }