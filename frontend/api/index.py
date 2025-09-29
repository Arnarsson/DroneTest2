"""
Vercel serverless handler for FastAPI app
This wraps the FastAPI app to work with Vercel's Python runtime
"""
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app
from main import app
from mangum import Mangum

# Create handler using Mangum adapter
handler = Mangum(app, lifespan="off")