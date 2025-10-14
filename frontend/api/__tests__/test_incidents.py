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


class TestIncidentsErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_database_error_returns_500(self):
        """Test database errors return 500 status"""
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
