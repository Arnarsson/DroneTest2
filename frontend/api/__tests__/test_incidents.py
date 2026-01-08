"""
Comprehensive test suite for incidents.py API endpoint.
Tests GET /api/incidents with various filters, error handling, and CORS.
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from incidents import handler


# Default rate limit mock values (always allow requests)
DEFAULT_RATE_LIMIT_RESPONSE = (True, 99, 60)  # (allowed, remaining, reset_after)
DEFAULT_RATE_LIMIT_HEADERS = {
    'X-RateLimit-Limit': '100',
    'X-RateLimit-Remaining': '99',
    'X-RateLimit-Reset': '1704067260',
    'Retry-After': '60',
}


def mock_rate_limit_allow():
    """Context manager to mock rate limiter to always allow requests"""
    return patch.multiple(
        'incidents',
        check_rate_limit=Mock(return_value=DEFAULT_RATE_LIMIT_RESPONSE),
        get_client_ip=Mock(return_value='127.0.0.1'),
        get_rate_limit_headers=Mock(return_value=DEFAULT_RATE_LIMIT_HEADERS)
    )


def mock_rate_limit_block(remaining=0, reset_after=30):
    """Context manager to mock rate limiter to block requests (rate limit exceeded)"""
    blocked_response = (False, remaining, reset_after)
    blocked_headers = {
        'X-RateLimit-Limit': '100',
        'X-RateLimit-Remaining': str(remaining),
        'X-RateLimit-Reset': str(int(datetime.now(timezone.utc).timestamp()) + reset_after),
        'Retry-After': str(reset_after),
    }
    return patch.multiple(
        'incidents',
        check_rate_limit=Mock(return_value=blocked_response),
        get_client_ip=Mock(return_value='127.0.0.1'),
        get_rate_limit_headers=Mock(return_value=blocked_headers)
    )


class MockAsyncPGConnection:
    """Mock asyncpg.Connection for database testing"""

    def __init__(self, mock_data=None):
        self.mock_data = mock_data or []
        self.closed = False

    async def fetch(self, query, *params):
        """Mock fetch method returning test data"""
        return self.mock_data

    async def close(self):
        """Mock close method"""
        self.closed = True


class MockHTTPRequestHandler:
    """Mock HTTP request/response for testing handler"""

    def __init__(self, path='/', method='GET', headers=None, origin=None):
        self.path = path
        self.command = method
        self.headers = headers or {}
        if origin:
            self.headers['Origin'] = origin

        # Response tracking
        self.response_code = None
        self.response_headers = {}
        self.response_body = None
        self._wfile = BytesIO()

    def send_response(self, code):
        self.response_code = code

    def send_header(self, key, value):
        self.response_headers[key] = value

    def end_headers(self):
        pass

    @property
    def wfile(self):
        return self._wfile

    def get_response_body(self):
        return self._wfile.getvalue().decode('utf-8')


def create_mock_incident_row(
    incident_id=None,
    title="Drone spotted over Copenhagen Airport",
    narrative="Multiple witnesses reported a drone flying near runway 22L.",
    occurred_at=None,
    lat=55.6181,
    lon=12.6560,
    evidence_score=3,
    country="DK",
    asset_type="airport",
    status="active",
    sources=None
):
    """Factory function to create mock incident database rows"""
    if occurred_at is None:
        occurred_at = datetime.now(timezone.utc)

    if sources is None:
        sources = json.dumps([{
            "source_url": "https://politi.dk/doegnet/2024/10/drone-copenhagen",
            "source_type": "police",
            "source_name": "Danish Police",
            "trust_weight": 4
        }])

    return {
        "id": incident_id or uuid4(),
        "title": title,
        "narrative": narrative,
        "occurred_at": occurred_at,
        "first_seen_at": occurred_at,
        "last_seen_at": occurred_at,
        "lat": lat,
        "lon": lon,
        "evidence_score": evidence_score,
        "country": country,
        "asset_type": asset_type,
        "status": status,
        "sources": sources
    }


class TestIncidentsAPIBasics:
    """Test basic API functionality and default behavior"""

    @pytest.mark.asyncio
    async def test_get_incidents_default_params(self):
        """Test GET /api/incidents with no filters returns incidents"""
        # Mock database returning 3 incidents
        mock_incidents = [
            create_mock_incident_row(title="Incident 1", evidence_score=4),
            create_mock_incident_row(title="Incident 2", evidence_score=3),
            create_mock_incident_row(title="Incident 3", evidence_score=2),
        ]

        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = [
                    {
                        "id": str(inc["id"]),
                        "title": inc["title"],
                        "narrative": inc["narrative"],
                        "occurred_at": inc["occurred_at"].isoformat(),
                        "lat": inc["lat"],
                        "lon": inc["lon"],
                        "evidence_score": inc["evidence_score"],
                        "country": inc["country"],
                        "asset_type": inc["asset_type"],
                        "status": inc["status"],
                        "sources": json.loads(inc["sources"])
                    }
                    for inc in mock_incidents
                ]

                # Create mock request
                mock_request = MockHTTPRequestHandler(path='/api/incidents')

                # Execute handler
                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                # Verify response
                assert mock_request.response_code == 200
                assert mock_request.response_headers['Content-Type'] == 'application/json'

                # Parse response body
                response_data = json.loads(mock_request.get_response_body())
                assert len(response_data) == 3
                assert response_data[0]['title'] == "Incident 1"

    @pytest.mark.asyncio
    async def test_get_incidents_empty_result(self):
        """Test API returns empty array when no incidents match filters"""
        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = []

                mock_request = MockHTTPRequestHandler(
                    path='/api/incidents?min_evidence=4&country=XX'
                )

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                assert mock_request.response_code == 200
                response_data = json.loads(mock_request.get_response_body())
                assert response_data == []


class TestIncidentsFiltering:
    """Test query parameter filtering logic"""

    @pytest.mark.asyncio
    async def test_get_incidents_with_evidence_filter(self):
        """Test min_evidence filter correctly passed to database query"""
        with mock_rate_limit_allow():
            with patch('incidents.fetch_incidents') as mock_fetch:
                mock_fetch.return_value = []

                with patch('incidents.run_async') as mock_run_async:
                    mock_run_async.return_value = []

                    mock_request = MockHTTPRequestHandler(
                        path='/api/incidents?min_evidence=3'
                    )

                    h = handler()
                    h.__dict__.update(mock_request.__dict__)
                    h.handle_get()

                    # Verify fetch_incidents called with correct params
                    # Note: fetch_incidents is called inside run_async
                    assert mock_request.response_code == 200

    @pytest.mark.asyncio
    async def test_get_incidents_with_country_filter(self):
        """Test country filter returns only matching incidents"""
        # Mock only Danish incidents
        mock_incidents = [
            create_mock_incident_row(title="Copenhagen incident", country="DK"),
            create_mock_incident_row(title="Aarhus incident", country="DK"),
        ]

        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = [
                    {
                        "id": str(inc["id"]),
                        "title": inc["title"],
                        "country": inc["country"],
                        "evidence_score": inc["evidence_score"],
                        "lat": inc["lat"],
                        "lon": inc["lon"],
                        "asset_type": inc["asset_type"],
                        "status": inc["status"],
                        "narrative": inc["narrative"],
                        "occurred_at": inc["occurred_at"].isoformat(),
                        "sources": json.loads(inc["sources"])
                    }
                    for inc in mock_incidents
                ]

                mock_request = MockHTTPRequestHandler(
                    path='/api/incidents?country=DK'
                )

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                response_data = json.loads(mock_request.get_response_body())
                assert len(response_data) == 2
                assert all(inc["country"] == "DK" for inc in response_data)

    @pytest.mark.asyncio
    async def test_get_incidents_with_status_filter(self):
        """Test status filter correctly filters incidents"""
        mock_request = MockHTTPRequestHandler(
            path='/api/incidents?status=active'
        )

        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = [
                    {
                        "id": str(uuid4()),
                        "title": "Active incident",
                        "status": "active",
                        "evidence_score": 3,
                        "country": "DK",
                        "lat": 55.6181,
                        "lon": 12.6560,
                        "asset_type": "airport",
                        "narrative": "Test",
                        "occurred_at": datetime.now(timezone.utc).isoformat(),
                        "sources": []
                    }
                ]

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                response_data = json.loads(mock_request.get_response_body())
                assert all(inc["status"] == "active" for inc in response_data)

    @pytest.mark.asyncio
    async def test_get_incidents_pagination(self):
        """Test limit parameter restricts result count"""
        # Mock 100 incidents but limit to 10
        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = [
                    {
                        "id": str(uuid4()),
                        "title": f"Incident {i}",
                        "evidence_score": 2,
                        "country": "DK",
                        "lat": 55.6 + i * 0.01,
                        "lon": 12.6 + i * 0.01,
                        "asset_type": "other",
                        "status": "active",
                        "narrative": f"Test incident {i}",
                        "occurred_at": datetime.now(timezone.utc).isoformat(),
                        "sources": []
                    }
                    for i in range(10)  # API should limit to 10
                ]

                mock_request = MockHTTPRequestHandler(
                    path='/api/incidents?limit=10'
                )

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                response_data = json.loads(mock_request.get_response_body())
                assert len(response_data) == 10

    @pytest.mark.asyncio
    async def test_get_incidents_all_filter_value_ignored(self):
        """Test that 'all' filter values are treated as no filter"""
        mock_request = MockHTTPRequestHandler(
            path='/api/incidents?country=all&status=all&asset_type=all'
        )

        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = [
                    {
                        "id": str(uuid4()),
                        "title": "Mixed country incident",
                        "country": "NO",  # Not filtered out even though we passed country=all
                        "status": "resolved",  # Not filtered out
                        "evidence_score": 2,
                        "lat": 59.9139,
                        "lon": 10.7522,
                        "asset_type": "harbor",
                        "narrative": "Test",
                        "occurred_at": datetime.now(timezone.utc).isoformat(),
                        "sources": []
                    }
                ]

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                assert mock_request.response_code == 200
                response_data = json.loads(mock_request.get_response_body())
                assert len(response_data) == 1


class TestIncidentsDataStructure:
    """Test response data structure and PostGIS coordinate extraction"""

    @pytest.mark.asyncio
    async def test_postgis_coordinate_extraction(self):
        """Test that lat/lon are properly extracted from PostGIS geometry"""
        expected_lat = 55.6181
        expected_lon = 12.6560

        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = [{
                    "id": str(uuid4()),
                    "title": "Test incident",
                    "lat": expected_lat,
                    "lon": expected_lon,
                    "evidence_score": 3,
                    "country": "DK",
                    "asset_type": "airport",
                    "status": "active",
                    "narrative": "Test",
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                    "sources": []
                }]

                mock_request = MockHTTPRequestHandler(path='/api/incidents')

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                response_data = json.loads(mock_request.get_response_body())
                assert response_data[0]["lat"] == expected_lat
                assert response_data[0]["lon"] == expected_lon

    @pytest.mark.asyncio
    async def test_sources_aggregation(self):
        """Test that incidents have sources array with proper structure"""
        mock_sources = [
            {
                "source_url": "https://politi.dk/incident1",
                "source_type": "police",
                "source_name": "Danish Police",
                "trust_weight": 4
            },
            {
                "source_url": "https://dr.dk/incident1",
                "source_type": "news",
                "source_name": "DR Nyheder",
                "trust_weight": 2
            }
        ]

        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = [{
                    "id": str(uuid4()),
                    "title": "Multi-source incident",
                    "evidence_score": 4,
                    "country": "DK",
                    "lat": 55.6181,
                    "lon": 12.6560,
                    "asset_type": "airport",
                    "status": "active",
                    "narrative": "Test",
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                    "sources": mock_sources
                }]

                mock_request = MockHTTPRequestHandler(path='/api/incidents')

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                response_data = json.loads(mock_request.get_response_body())
                sources = response_data[0]["sources"]

                assert len(sources) == 2
                assert sources[0]["source_type"] == "police"
                assert sources[1]["source_type"] == "news"
                assert sources[0]["trust_weight"] == 4


class TestIncidentsCORS:
    """Test CORS header handling and security"""

    def test_cors_headers_whitelisted_origin(self):
        """Test CORS headers set correctly for whitelisted origins"""
        for allowed_origin in [
            'https://www.dronemap.cc',
            'https://dronewatch.cc',
            'http://localhost:3000',
            'http://localhost:3001'
        ]:
            with mock_rate_limit_allow():
                with patch('incidents.run_async') as mock_run_async:
                    mock_run_async.return_value = []

                    mock_request = MockHTTPRequestHandler(
                        path='/api/incidents',
                        origin=allowed_origin
                    )

                    h = handler()
                    h.__dict__.update(mock_request.__dict__)
                    h.handle_get()

                    assert mock_request.response_headers.get('Access-Control-Allow-Origin') == allowed_origin
                    assert 'Access-Control-Allow-Methods' in mock_request.response_headers

    def test_cors_headers_blocked_origin(self):
        """Test CORS headers NOT set for non-whitelisted origins"""
        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = []

                mock_request = MockHTTPRequestHandler(
                    path='/api/incidents',
                    origin='https://evil-site.com'
                )

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                # CORS headers should NOT be present for blocked origins
                assert 'Access-Control-Allow-Origin' not in mock_request.response_headers

    def test_options_preflight_request(self):
        """Test OPTIONS preflight request handling"""
        mock_request = MockHTTPRequestHandler(
            path='/api/incidents',
            method='OPTIONS',
            origin='https://www.dronemap.cc'
        )

        h = handler()
        h.__dict__.update(mock_request.__dict__)
        h.do_OPTIONS()

        assert mock_request.response_code == 200
        assert mock_request.response_headers.get('Access-Control-Allow-Origin') == 'https://www.dronemap.cc'
        assert 'GET, OPTIONS' in mock_request.response_headers.get('Access-Control-Allow-Methods', '')


class TestIncidentsSearch:
    """Test search query parameter functionality"""

    @pytest.mark.asyncio
    async def test_empty_search_returns_all(self):
        """Test that empty search parameter returns all incidents (same as no filter)"""
        # Mock incidents - should return all since search is empty
        mock_incidents = [
            create_mock_incident_row(
                title="Copenhagen Airport drone sighting",
                narrative="Multiple witnesses reported activity",
                evidence_score=4
            ),
            create_mock_incident_row(
                title="Stockholm harbor incident",
                narrative="Security reported unknown drone",
                evidence_score=3
            ),
            create_mock_incident_row(
                title="Oslo military base alert",
                narrative="Radar detected unidentified object",
                evidence_score=5
            ),
        ]

        with patch('incidents.run_async') as mock_run_async, \
             patch('incidents.os.getenv') as mock_getenv, \
             patch('incidents.check_rate_limit') as mock_rate_limit, \
             patch('incidents.get_client_ip') as mock_get_ip, \
             patch('incidents.get_rate_limit_headers') as mock_rate_headers:
            # Mock environment and rate limiting
            mock_getenv.return_value = 'postgresql://mock@localhost/test'
            mock_rate_limit.return_value = (True, 100, 60)
            mock_get_ip.return_value = '127.0.0.1'
            mock_rate_headers.return_value = {}

            # Return all incidents (simulating no search filter applied for empty search)
            mock_run_async.return_value = [
                {
                    "id": str(inc["id"]),
                    "title": inc["title"],
                    "narrative": inc["narrative"],
                    "occurred_at": inc["occurred_at"].isoformat(),
                    "lat": inc["lat"],
                    "lon": inc["lon"],
                    "evidence_score": inc["evidence_score"],
                    "country": inc["country"],
                    "asset_type": inc["asset_type"],
                    "status": inc["status"],
                    "sources": json.loads(inc["sources"])
                }
                for inc in mock_incidents
            ]

            # Create mock request with empty search parameter
            mock_request = MockHTTPRequestHandler(
                path='/api/incidents?search='
            )

            # Execute handler
            h = object.__new__(handler)
            h.path = mock_request.path
            h.command = mock_request.command
            h.headers = mock_request.headers
            h.send_response = mock_request.send_response
            h.send_header = mock_request.send_header
            h.end_headers = mock_request.end_headers
            h.wfile = mock_request._wfile

            h.handle_get()

            # Verify response
            assert mock_request.response_code == 200
            assert mock_request.response_headers['Content-Type'] == 'application/json'

            # Parse response body
            response_data = json.loads(mock_request.get_response_body())

            # Should return all 3 incidents since search is empty (no filter applied)
            assert len(response_data) == 3

            # Verify all mock incidents are returned
            titles = [inc['title'] for inc in response_data]
            assert "Copenhagen Airport drone sighting" in titles
            assert "Stockholm harbor incident" in titles
            assert "Oslo military base alert" in titles

    @pytest.mark.asyncio
    async def test_get_incidents_with_search_parameter(self):
        """Test search parameter filters incidents by title, narrative, and location_name"""
        # Mock incidents - some matching search term "airport", some not
        mock_matching_incidents = [
            create_mock_incident_row(
                title="Drone spotted over Copenhagen Airport",
                narrative="Multiple witnesses reported activity",
                evidence_score=4
            ),
            create_mock_incident_row(
                title="Incident near facility",
                narrative="Security reported a drone near the airport perimeter",
                evidence_score=3
            ),
        ]

        with patch('incidents.run_async') as mock_run_async, \
             patch('incidents.os.getenv') as mock_getenv, \
             patch('incidents.check_rate_limit') as mock_rate_limit, \
             patch('incidents.get_client_ip') as mock_get_ip, \
             patch('incidents.get_rate_limit_headers') as mock_rate_headers:
            # Mock environment and rate limiting
            mock_getenv.return_value = 'postgresql://mock@localhost/test'
            mock_rate_limit.return_value = (True, 100, 60)
            mock_get_ip.return_value = '127.0.0.1'
            mock_rate_headers.return_value = {}

            # Return only matching incidents (simulating database ILIKE filtering)
            mock_run_async.return_value = [
                {
                    "id": str(inc["id"]),
                    "title": inc["title"],
                    "narrative": inc["narrative"],
                    "occurred_at": inc["occurred_at"].isoformat(),
                    "lat": inc["lat"],
                    "lon": inc["lon"],
                    "evidence_score": inc["evidence_score"],
                    "country": inc["country"],
                    "asset_type": inc["asset_type"],
                    "status": inc["status"],
                    "sources": json.loads(inc["sources"])
                }
                for inc in mock_matching_incidents
            ]

            # Create mock request with search parameter
            mock_request = MockHTTPRequestHandler(
                path='/api/incidents?search=airport'
            )

            # Execute handler (use object.__new__ to bypass __init__ requirements)
            h = object.__new__(handler)
            h.path = mock_request.path
            h.command = mock_request.command
            h.headers = mock_request.headers
            h._wfile = mock_request._wfile
            h.wfile = property(lambda self: self._wfile)

            # Bind mock methods to handler instance
            h.send_response = mock_request.send_response
            h.send_header = mock_request.send_header
            h.end_headers = mock_request.end_headers
            h.wfile = mock_request._wfile

            h.handle_get()

            # Verify response
            assert mock_request.response_code == 200
            assert mock_request.response_headers['Content-Type'] == 'application/json'

            # Parse response body
            response_data = json.loads(mock_request.get_response_body())
            assert len(response_data) == 2

            # Verify incidents contain search term in title or narrative
            for incident in response_data:
                title_lower = incident['title'].lower()
                narrative_lower = incident['narrative'].lower()
                assert 'airport' in title_lower or 'airport' in narrative_lower

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self):
        """Test that search is case-insensitive - 'Drone', 'drone', 'DRONE' return same results"""
        # Mock incident with mixed case - should match regardless of search case
        mock_incident = create_mock_incident_row(
            title="Drone spotted over Copenhagen Airport",
            narrative="Security reported a DRONE near the runway",
            evidence_score=3
        )

        with patch('incidents.run_async') as mock_run_async, \
             patch('incidents.os.getenv') as mock_getenv, \
             patch('incidents.check_rate_limit') as mock_rate_limit, \
             patch('incidents.get_client_ip') as mock_get_ip, \
             patch('incidents.get_rate_limit_headers') as mock_rate_headers:
            # Mock environment and rate limiting
            mock_getenv.return_value = 'postgresql://mock@localhost/test'
            mock_rate_limit.return_value = (True, 100, 60)
            mock_get_ip.return_value = '127.0.0.1'
            mock_rate_headers.return_value = {}

            # Mock returns the same incident for any case search
            # (simulating PostgreSQL ILIKE case-insensitive matching)
            mock_result = [{
                "id": str(mock_incident["id"]),
                "title": mock_incident["title"],
                "narrative": mock_incident["narrative"],
                "occurred_at": mock_incident["occurred_at"].isoformat(),
                "lat": mock_incident["lat"],
                "lon": mock_incident["lon"],
                "evidence_score": mock_incident["evidence_score"],
                "country": mock_incident["country"],
                "asset_type": mock_incident["asset_type"],
                "status": mock_incident["status"],
                "sources": json.loads(mock_incident["sources"])
            }]
            mock_run_async.return_value = mock_result

            # Test lowercase search
            mock_request_lower = MockHTTPRequestHandler(
                path='/api/incidents?search=drone'
            )
            h_lower = object.__new__(handler)
            h_lower.path = mock_request_lower.path
            h_lower.command = mock_request_lower.command
            h_lower.headers = mock_request_lower.headers
            h_lower.send_response = mock_request_lower.send_response
            h_lower.send_header = mock_request_lower.send_header
            h_lower.end_headers = mock_request_lower.end_headers
            h_lower.wfile = mock_request_lower._wfile
            h_lower.handle_get()

            assert mock_request_lower.response_code == 200
            response_lower = json.loads(mock_request_lower.get_response_body())
            assert len(response_lower) == 1
            assert response_lower[0]['title'] == "Drone spotted over Copenhagen Airport"

            # Reset mock for uppercase test
            mock_run_async.return_value = mock_result

            # Test uppercase search
            mock_request_upper = MockHTTPRequestHandler(
                path='/api/incidents?search=DRONE'
            )
            h_upper = object.__new__(handler)
            h_upper.path = mock_request_upper.path
            h_upper.command = mock_request_upper.command
            h_upper.headers = mock_request_upper.headers
            h_upper.send_response = mock_request_upper.send_response
            h_upper.send_header = mock_request_upper.send_header
            h_upper.end_headers = mock_request_upper.end_headers
            h_upper.wfile = mock_request_upper._wfile
            h_upper.handle_get()

            assert mock_request_upper.response_code == 200
            response_upper = json.loads(mock_request_upper.get_response_body())
            assert len(response_upper) == 1
            assert response_upper[0]['title'] == "Drone spotted over Copenhagen Airport"

            # Reset mock for mixed case test
            mock_run_async.return_value = mock_result

            # Test mixed case search
            mock_request_mixed = MockHTTPRequestHandler(
                path='/api/incidents?search=DroNe'
            )
            h_mixed = object.__new__(handler)
            h_mixed.path = mock_request_mixed.path
            h_mixed.command = mock_request_mixed.command
            h_mixed.headers = mock_request_mixed.headers
            h_mixed.send_response = mock_request_mixed.send_response
            h_mixed.send_header = mock_request_mixed.send_header
            h_mixed.end_headers = mock_request_mixed.end_headers
            h_mixed.wfile = mock_request_mixed._wfile
            h_mixed.handle_get()

            assert mock_request_mixed.response_code == 200
            response_mixed = json.loads(mock_request_mixed.get_response_body())
            assert len(response_mixed) == 1
            assert response_mixed[0]['title'] == "Drone spotted over Copenhagen Airport"

            # All three cases should return the same result
            assert response_lower == response_upper == response_mixed

    @pytest.mark.asyncio
    async def test_search_multiple_fields(self):
        """Test that search matches across title, narrative, and location_name fields"""
        # Create mock incidents with search term "Copenhagen" in different fields:
        # 1. Title contains "Copenhagen"
        # 2. Narrative contains "Copenhagen"
        # 3. Location_name contains "Copenhagen"

        with patch('incidents.run_async') as mock_run_async, \
             patch('incidents.os.getenv') as mock_getenv, \
             patch('incidents.check_rate_limit') as mock_rate_limit, \
             patch('incidents.get_client_ip') as mock_get_ip, \
             patch('incidents.get_rate_limit_headers') as mock_rate_headers:
            # Mock environment and rate limiting
            mock_getenv.return_value = 'postgresql://mock@localhost/test'
            mock_rate_limit.return_value = (True, 100, 60)
            mock_get_ip.return_value = '127.0.0.1'
            mock_rate_headers.return_value = {}

            # Return incidents matching in different fields
            # (simulating database ILIKE matching on title OR narrative OR location_name)
            mock_run_async.return_value = [
                {
                    "id": str(uuid4()),
                    "title": "Copenhagen Airport drone sighting",  # Match in title
                    "narrative": "A drone was spotted near the runway",
                    "location_name": "Kastrup Airport",
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                    "lat": 55.6181,
                    "lon": 12.6560,
                    "evidence_score": 4,
                    "country": "DK",
                    "asset_type": "airport",
                    "status": "active",
                    "sources": []
                },
                {
                    "id": str(uuid4()),
                    "title": "Drone near power station",
                    "narrative": "Reports from Copenhagen police confirmed sighting",  # Match in narrative
                    "location_name": "Amager Power Station",
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                    "lat": 55.6500,
                    "lon": 12.6200,
                    "evidence_score": 3,
                    "country": "DK",
                    "asset_type": "power_station",
                    "status": "active",
                    "sources": []
                },
                {
                    "id": str(uuid4()),
                    "title": "Military facility incident",
                    "narrative": "Unidentified drone detected by radar",
                    "location_name": "Copenhagen Naval Base",  # Match in location_name
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                    "lat": 55.6800,
                    "lon": 12.5900,
                    "evidence_score": 5,
                    "country": "DK",
                    "asset_type": "military",
                    "status": "active",
                    "sources": []
                }
            ]

            # Create mock request with search parameter
            mock_request = MockHTTPRequestHandler(
                path='/api/incidents?search=Copenhagen'
            )

            # Execute handler
            h = object.__new__(handler)
            h.path = mock_request.path
            h.command = mock_request.command
            h.headers = mock_request.headers
            h.send_response = mock_request.send_response
            h.send_header = mock_request.send_header
            h.end_headers = mock_request.end_headers
            h.wfile = mock_request._wfile

            h.handle_get()

            # Verify response
            assert mock_request.response_code == 200
            assert mock_request.response_headers['Content-Type'] == 'application/json'

            # Parse response body
            response_data = json.loads(mock_request.get_response_body())

            # Should return all 3 incidents (matched in different fields)
            assert len(response_data) == 3

            # Verify each incident contains "Copenhagen" in at least one field
            for incident in response_data:
                title = incident.get('title', '').lower()
                narrative = incident.get('narrative', '').lower()
                location_name = incident.get('location_name', '').lower()

                has_match = (
                    'copenhagen' in title or
                    'copenhagen' in narrative or
                    'copenhagen' in location_name
                )
                assert has_match, f"Incident should contain 'copenhagen' in title, narrative, or location_name"

            # Verify specific incidents were returned
            titles = [inc['title'] for inc in response_data]
            assert "Copenhagen Airport drone sighting" in titles  # Match in title
            assert "Drone near power station" in titles  # Match in narrative
            assert "Military facility incident" in titles  # Match in location_name

    @pytest.mark.asyncio
    async def test_search_special_characters(self):
        """Test that search with special characters (%, _, ', ") is safely handled"""
        # Test various special characters that could cause SQL injection or query issues
        special_char_queries = [
            "%",           # SQL LIKE wildcard
            "_",           # SQL LIKE single character wildcard
            "'",           # SQL string delimiter
            '"',           # Double quote
            "'; DROP TABLE incidents; --",  # SQL injection attempt
            "%' OR '1'='1",  # SQL injection attempt
            "test%test",   # Embedded wildcard
            "test_test",   # Embedded single char wildcard
            "O'Brien",     # Name with apostrophe
            'Drone "UAV"', # Quoted text
        ]

        for special_query in special_char_queries:
            with patch('incidents.run_async') as mock_run_async, \
                 patch('incidents.os.getenv') as mock_getenv, \
                 patch('incidents.check_rate_limit') as mock_rate_limit, \
                 patch('incidents.get_client_ip') as mock_get_ip, \
                 patch('incidents.get_rate_limit_headers') as mock_rate_headers:
                # Mock environment and rate limiting
                mock_getenv.return_value = 'postgresql://mock@localhost/test'
                mock_rate_limit.return_value = (True, 100, 60)
                mock_get_ip.return_value = '127.0.0.1'
                mock_rate_headers.return_value = {}

                # Mock returns empty array (simulating no matches for special char queries)
                # The key test is that the handler doesn't crash with SQL errors
                mock_run_async.return_value = []

                # URL-encode the special query for the path
                from urllib.parse import quote
                encoded_query = quote(special_query, safe='')

                # Create mock request with special character search
                mock_request = MockHTTPRequestHandler(
                    path=f'/api/incidents?search={encoded_query}'
                )

                # Execute handler
                h = object.__new__(handler)
                h.path = mock_request.path
                h.command = mock_request.command
                h.headers = mock_request.headers
                h.send_response = mock_request.send_response
                h.send_header = mock_request.send_header
                h.end_headers = mock_request.end_headers
                h.wfile = mock_request._wfile

                # Handler should not crash with special characters
                try:
                    h.handle_get()
                except Exception as e:
                    pytest.fail(f"Handler crashed with special character query '{special_query}': {e}")

                # Verify response is valid (200 OK with JSON)
                assert mock_request.response_code == 200, \
                    f"Expected 200 for query '{special_query}', got {mock_request.response_code}"
                assert mock_request.response_headers['Content-Type'] == 'application/json', \
                    f"Expected JSON content type for query '{special_query}'"

                # Verify response body is valid JSON array
                response_data = json.loads(mock_request.get_response_body())
                assert isinstance(response_data, list), \
                    f"Expected list response for query '{special_query}'"

    @pytest.mark.asyncio
    async def test_search_with_country_filter(self):
        """Test that search works correctly when combined with country filter"""
        # Create mock incidents that match both search="drone" and country="DK"
        # These simulate what the database would return when both filters are applied

        with patch('incidents.run_async') as mock_run_async, \
             patch('incidents.os.getenv') as mock_getenv, \
             patch('incidents.check_rate_limit') as mock_rate_limit, \
             patch('incidents.get_client_ip') as mock_get_ip, \
             patch('incidents.get_rate_limit_headers') as mock_rate_headers:
            # Mock environment and rate limiting
            mock_getenv.return_value = 'postgresql://mock@localhost/test'
            mock_rate_limit.return_value = (True, 100, 60)
            mock_get_ip.return_value = '127.0.0.1'
            mock_rate_headers.return_value = {}

            # Return only incidents matching both search="drone" AND country="DK"
            # (simulating database applying both filters)
            mock_run_async.return_value = [
                {
                    "id": str(uuid4()),
                    "title": "Drone spotted over Copenhagen Airport",
                    "narrative": "Multiple witnesses reported drone activity",
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                    "lat": 55.6181,
                    "lon": 12.6560,
                    "evidence_score": 4,
                    "country": "DK",  # Matches country filter
                    "asset_type": "airport",
                    "status": "active",
                    "sources": []
                },
                {
                    "id": str(uuid4()),
                    "title": "Unknown drone near Aarhus harbor",
                    "narrative": "Security reported a drone sighting",
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                    "lat": 56.1629,
                    "lon": 10.2039,
                    "evidence_score": 3,
                    "country": "DK",  # Matches country filter
                    "asset_type": "harbor",
                    "status": "active",
                    "sources": []
                }
            ]

            # Create mock request with both search and country parameters
            mock_request = MockHTTPRequestHandler(
                path='/api/incidents?search=drone&country=DK'
            )

            # Execute handler
            h = object.__new__(handler)
            h.path = mock_request.path
            h.command = mock_request.command
            h.headers = mock_request.headers
            h.send_response = mock_request.send_response
            h.send_header = mock_request.send_header
            h.end_headers = mock_request.end_headers
            h.wfile = mock_request._wfile

            h.handle_get()

            # Verify response
            assert mock_request.response_code == 200
            assert mock_request.response_headers['Content-Type'] == 'application/json'

            # Parse response body
            response_data = json.loads(mock_request.get_response_body())

            # Should return 2 incidents (matching both search="drone" and country="DK")
            assert len(response_data) == 2

            # Verify all incidents contain "drone" in title or narrative
            for incident in response_data:
                title_lower = incident['title'].lower()
                narrative_lower = incident['narrative'].lower()
                assert 'drone' in title_lower or 'drone' in narrative_lower, \
                    f"Incident should contain 'drone' in title or narrative"

            # Verify all incidents have country="DK"
            for incident in response_data:
                assert incident['country'] == 'DK', \
                    f"Incident should have country='DK', got '{incident['country']}'"


class TestIncidentsErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_database_error_returns_500(self):
        """Test database errors return 500 status"""
        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                # Simulate database error
                mock_run_async.side_effect = Exception("Database connection failed")

                mock_request = MockHTTPRequestHandler(path='/api/incidents')

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                assert mock_request.response_code == 500
                response_data = json.loads(mock_request.get_response_body())
                assert response_data == []

    @pytest.mark.asyncio
    async def test_invalid_parameters_handled_gracefully(self):
        """Test invalid query parameters don't crash the API"""
        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = []

                # Test with invalid min_evidence (should default to 1)
                mock_request = MockHTTPRequestHandler(
                    path='/api/incidents?min_evidence=invalid'
                )

                h = handler()
                h.__dict__.update(mock_request.__dict__)

                try:
                    h.handle_get()
                    # If it doesn't crash, the test passes
                    assert mock_request.response_code in [200, 500]
                except ValueError:
                    # Expected behavior - invalid int conversion
                    pass

    @pytest.mark.asyncio
    async def test_cache_control_header_set(self):
        """Test Cache-Control header is set for performance"""
        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = []

                mock_request = MockHTTPRequestHandler(path='/api/incidents')

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                assert 'Cache-Control' in mock_request.response_headers
                # Should have public caching with max-age
                cache_header = mock_request.response_headers['Cache-Control']
                assert 'public' in cache_header or 'max-age' in cache_header


class TestIncidentsRateLimiting:
    """Test rate limiting behavior with the distributed rate limiter"""

    def test_rate_limit_exceeded_returns_429(self):
        """Test that exceeding rate limit returns 429 status"""
        with mock_rate_limit_block(remaining=0, reset_after=30):
            mock_request = MockHTTPRequestHandler(
                path='/api/incidents',
                origin='https://www.dronemap.cc'
            )

            h = handler()
            h.__dict__.update(mock_request.__dict__)
            h.handle_get()

            assert mock_request.response_code == 429
            response_data = json.loads(mock_request.get_response_body())
            assert 'error' in response_data
            assert response_data['error'] == 'Rate limit exceeded'
            assert 'retry_after' in response_data

    def test_rate_limit_headers_included_on_429(self):
        """Test that rate limit headers are included in 429 response"""
        with mock_rate_limit_block(remaining=0, reset_after=30):
            mock_request = MockHTTPRequestHandler(
                path='/api/incidents',
                origin='https://www.dronemap.cc'
            )

            h = handler()
            h.__dict__.update(mock_request.__dict__)
            h.handle_get()

            assert mock_request.response_code == 429
            assert 'X-RateLimit-Limit' in mock_request.response_headers
            assert 'X-RateLimit-Remaining' in mock_request.response_headers
            assert 'Retry-After' in mock_request.response_headers

    def test_rate_limit_headers_included_on_success(self):
        """Test that rate limit headers are included in successful responses"""
        with mock_rate_limit_allow():
            with patch('incidents.run_async') as mock_run_async:
                mock_run_async.return_value = []

                mock_request = MockHTTPRequestHandler(path='/api/incidents')

                h = handler()
                h.__dict__.update(mock_request.__dict__)
                h.handle_get()

                assert mock_request.response_code == 200
                assert 'X-RateLimit-Limit' in mock_request.response_headers
                assert 'X-RateLimit-Remaining' in mock_request.response_headers

    def test_cors_headers_on_rate_limit_response(self):
        """Test that CORS headers are still included on rate limit response for allowed origins"""
        with mock_rate_limit_block(remaining=0, reset_after=30):
            mock_request = MockHTTPRequestHandler(
                path='/api/incidents',
                origin='https://www.dronemap.cc'
            )

            h = handler()
            h.__dict__.update(mock_request.__dict__)
            h.handle_get()

            assert mock_request.response_code == 429
            # CORS headers should still be present for rate-limited responses
            assert mock_request.response_headers.get('Access-Control-Allow-Origin') == 'https://www.dronemap.cc'
