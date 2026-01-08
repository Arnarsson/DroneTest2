from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with error handling to catch initialization failures
try:
    from db import fetch_incidents, run_async
    from rate_limit import get_client_ip, check_rate_limit, get_rate_limit_headers
except Exception as e:
    # Log import errors for debugging
    print(f"CRITICAL: Failed to import modules: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    # Re-raise to fail fast - Vercel will show this in logs
    raise

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_get()

    def do_OPTIONS(self):
        # Handle CORS preflight - whitelist specific origins only
        ALLOWED_ORIGINS = [
            'https://www.dronemap.cc',
            'https://dronemap.cc',
            'https://www.dronewatch.cc',
            'https://dronewatch.cc',
            'http://localhost:3000',
            'http://localhost:3001'
        ]

        origin = self.headers.get('Origin', '')
        self.send_response(200)

        # Only allow whitelisted origins
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Max-Age', '86400')

        self.end_headers()

    def handle_get(self):
        # Validate DATABASE_URL is set before processing
        if not os.getenv('DATABASE_URL'):
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            origin = self.headers.get('Origin', '')
            ALLOWED_ORIGINS = [
                'https://www.dronemap.cc',
                'https://dronemap.cc',
                'https://www.dronewatch.cc',
                'https://dronewatch.cc',
                'http://localhost:3000',
                'http://localhost:3001'
            ]
            if origin in ALLOWED_ORIGINS:
                self.send_header('Access-Control-Allow-Origin', origin)
            self.end_headers()
            error_response = {
                'error': 'Configuration error',
                'message': 'DATABASE_URL environment variable not set. Check Vercel environment variables.',
                'detail': 'This is a server configuration issue. Contact the administrator.'
            }
            self.wfile.write(json.dumps(error_response).encode())
            print("ERROR: DATABASE_URL not set", file=sys.stderr)
            return
        
        # Rate limiting check
        client_ip = get_client_ip(dict(self.headers))
        allowed, remaining, reset_after = check_rate_limit(client_ip)
        
        if not allowed:
            # Rate limit exceeded
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            
            # Add rate limit headers
            for key, value in get_rate_limit_headers(remaining, reset_after).items():
                self.send_header(key, value)
            
            # Handle CORS
            ALLOWED_ORIGINS = [
                'https://www.dronemap.cc',
                'https://dronemap.cc',
                'https://www.dronewatch.cc',
                'https://dronewatch.cc',
                'http://localhost:3000',
                'http://localhost:3001'
            ]
            origin = self.headers.get('Origin', '')
            if origin in ALLOWED_ORIGINS:
                self.send_header('Access-Control-Allow-Origin', origin)
            
            self.end_headers()
            error_response = {
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Please try again in {reset_after} seconds.',
                'retry_after': reset_after
            }
            self.wfile.write(json.dumps(error_response).encode())
            return
        
        # Parse query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Get parameters with defaults
        min_evidence = int(query_params.get('min_evidence', ['1'])[0])
        limit = min(int(query_params.get('limit', ['200'])[0]), 1000)
        offset = int(query_params.get('offset', ['0'])[0])
        status = query_params.get('status', [None])[0]
        country = query_params.get('country', [None])[0]
        asset_type = query_params.get('asset_type', [None])[0]
        since = query_params.get('since', [None])[0]
        search = query_params.get('search', [None])[0]

        # Handle 'all' values as no filter
        if status == 'all':
            status = None
        if country == 'all':
            country = None
        if asset_type == 'all' or asset_type == '':
            asset_type = None

        # Fetch incidents from database
        error_detail = None
        try:
            result = run_async(fetch_incidents(
                min_evidence=min_evidence,
                limit=limit,
                offset=offset,
                status=status,
                country=country,
                asset_type=asset_type,
                since=since,
                search=search
            ))

            # Check if it's an error response
            if isinstance(result, dict) and 'error' in result:
                incidents = []
                status_code = 500
                error_detail = result.get('detail', result.get('error', 'Unknown error'))
            else:
                incidents = result
                status_code = 200
        except ValueError as e:
            # Database connection errors (missing DATABASE_URL, invalid format)
            print(f"Database configuration error: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            incidents = []
            status_code = 500
            error_detail = str(e)
        except Exception as e:
            # Other unexpected errors
            print(f"Error fetching incidents: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            incidents = []
            status_code = 500
            error_detail = "Internal server error"

        # Handle CORS - whitelist specific origins only
        ALLOWED_ORIGINS = [
            'https://www.dronemap.cc',
            'https://dronemap.cc',
            'https://www.dronewatch.cc',
            'https://dronewatch.cc',
            'http://localhost:3000',
            'http://localhost:3001'
        ]

        origin = self.headers.get('Origin', '')

        # Send response
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        
        # Only add cache headers for successful responses
        if status_code == 200:
            self.send_header('Cache-Control', 'public, max-age=15')
        
        # Add rate limit headers
        for key, value in get_rate_limit_headers(remaining, reset_after).items():
            self.send_header(key, value)

        # Only allow whitelisted origins
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        self.end_headers()
        
        # Return error response if there was an error
        if status_code != 200:
            error_response = {
                'error': 'Failed to fetch incidents',
                'message': error_detail if error_detail else 'Unknown error occurred',
                'status_code': status_code
            }
            self.wfile.write(json.dumps(error_response).encode())
        else:
            self.wfile.write(json.dumps(incidents).encode())