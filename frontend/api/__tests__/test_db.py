"""
Comprehensive test suite for db.py utilities.
Tests database connection, query optimization, and PostGIS operations.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from db import fetch_incidents, run_async
from db_utils import get_connection


class MockAsyncPGConnection:
    """Mock asyncpg.Connection for database testing"""

    def __init__(self, mock_data=None, should_timeout=False, should_error=False):
        self.mock_data = mock_data or []
        self.should_timeout = should_timeout
        self.should_error = should_error
        self.closed = False
        self.fetch_calls = []

    async def fetch(self, query, *params):
        """Mock fetch method"""
        self.fetch_calls.append((query, params))

        if self.should_timeout:
            await asyncio.sleep(10)  # Simulate timeout

        if self.should_error:
            import asyncpg
            raise asyncpg.exceptions.PostgresError("Database connection failed")

        return self.mock_data

    async def close(self):
        """Mock close method"""
        self.closed = True


def create_mock_row(**kwargs):
    """Helper to create mock database row"""
    defaults = {
        "id": uuid4(),
        "title": "Test incident",
        "narrative": "Test narrative",
        "occurred_at": datetime.now(timezone.utc),
        "first_seen_at": datetime.now(timezone.utc),
        "last_seen_at": datetime.now(timezone.utc),
        "lat": 55.6181,
        "lon": 12.6560,
        "evidence_score": 3,
        "country": "DK",
        "asset_type": "airport",
        "status": "active",
        "sources": []
    }
    defaults.update(kwargs)
    return defaults


class TestDatabaseConnection:
    """Test get_connection utility function"""

    @pytest.mark.asyncio
    async def test_get_connection_supabase_pooler_detection(self):
        """Test connection detects Supabase pooler (port 6543)"""
        database_url = "postgresql://user:pass@db.supabase.co:6543/postgres"

        with patch.dict(os.environ, {'DATABASE_URL': database_url}):
            with patch('db_utils.asyncpg.connect') as mock_connect:
                mock_connect.return_value = MockAsyncPGConnection()

                await get_connection()

                # Verify connection was called
                assert mock_connect.called

                # Check connection parameters
                call_args = mock_connect.call_args
                connection_params = call_args[1]

                # Should have pooler-specific settings
                assert connection_params.get('statement_cache_size') == 0
                assert connection_params.get('command_timeout') == 10
                assert connection_params.get('ssl') == 'require'

    @pytest.mark.asyncio
    async def test_get_connection_missing_env_var(self):
        """Test connection raises error when DATABASE_URL not set"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL.*not configured"):
                await get_connection()

    @pytest.mark.asyncio
    async def test_get_connection_non_supabase(self):
        """Test connection to non-Supabase database uses default settings"""
        database_url = "postgresql://localhost:5432/testdb"

        with patch.dict(os.environ, {'DATABASE_URL': database_url}):
            with patch('db_utils.asyncpg.connect') as mock_connect:
                mock_connect.return_value = MockAsyncPGConnection()

                await get_connection()

                # Should connect without Supabase-specific settings
                call_args = mock_connect.call_args
                connection_params = call_args[1]

                # No pooler settings for non-Supabase
                assert 'statement_cache_size' not in connection_params


class TestFetchIncidentsQueryOptimization:
    """Test query structure and performance optimizations"""

    @pytest.mark.asyncio
    async def test_fetch_incidents_uses_cte_structure(self):
        """Test fetch_incidents uses CTE for performance optimization"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents(min_evidence=2)

            # Verify query was executed
            assert len(mock_conn.fetch_calls) == 1

            query = mock_conn.fetch_calls[0][0]

            # Should use CTE (WITH clause)
            assert 'WITH filtered_incidents AS' in query
            assert 'incident_sources_agg AS' in query

    @pytest.mark.asyncio
    async def test_fetch_incidents_filter_before_aggregate(self):
        """Test filters applied to incidents BEFORE source aggregation"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents(
                min_evidence=3,
                country='DK',
                status='active'
            )

            query = mock_conn.fetch_calls[0][0]

            # Filters should be in filtered_incidents CTE, not after aggregation
            cte_section = query.split('incident_sources_agg')[0]

            assert 'evidence_score >=' in cte_section
            assert 'country =' in cte_section
            assert 'status =' in cte_section

    @pytest.mark.asyncio
    async def test_fetch_incidents_source_aggregation_optimization(self):
        """Test sources only aggregated for filtered incidents"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents(min_evidence=4)

            query = mock_conn.fetch_calls[0][0]

            # incident_sources_agg should filter by filtered_incidents
            assert 'WHERE is2.incident_id IN (SELECT id FROM filtered_incidents)' in query


class TestFetchIncidentsPostGIS:
    """Test PostGIS coordinate extraction"""

    @pytest.mark.asyncio
    async def test_postgis_lat_lon_extraction(self):
        """Test ST_X/ST_Y functions used for coordinate extraction"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            query = mock_conn.fetch_calls[0][0]

            # Should use PostGIS functions for coordinate extraction
            assert 'ST_Y(i.location::geometry) as lat' in query
            assert 'ST_X(i.location::geometry) as lon' in query

    @pytest.mark.asyncio
    async def test_fetch_incidents_returns_float_coordinates(self):
        """Test coordinates returned as float type"""
        mock_row = create_mock_row(lat=55.6181, lon=12.6560)

        mock_conn = MockAsyncPGConnection(mock_data=[mock_row])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            assert len(result) == 1
            assert isinstance(result[0]["lat"], float)
            assert isinstance(result[0]["lon"], float)
            assert result[0]["lat"] == 55.6181
            assert result[0]["lon"] == 12.6560


class TestFetchIncidentsFiltering:
    """Test query parameter filtering"""

    @pytest.mark.asyncio
    async def test_fetch_incidents_min_evidence_filter(self):
        """Test min_evidence parameter filters correctly"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents(min_evidence=3)

            query, params = mock_conn.fetch_calls[0]

            # First parameter should be min_evidence
            assert params[0] == 3
            assert 'evidence_score >= $1' in query

    @pytest.mark.asyncio
    async def test_fetch_incidents_country_filter(self):
        """Test country parameter added to query"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents(country='NO')

            query, params = mock_conn.fetch_calls[0]

            assert 'NO' in params
            assert 'country =' in query

    @pytest.mark.asyncio
    async def test_fetch_incidents_status_filter(self):
        """Test status parameter filtering"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents(status='resolved')

            query, params = mock_conn.fetch_calls[0]

            assert 'resolved' in params
            assert 'status =' in query

    @pytest.mark.asyncio
    async def test_fetch_incidents_asset_type_filter(self):
        """Test asset_type parameter filtering"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents(asset_type='military')

            query, params = mock_conn.fetch_calls[0]

            assert 'military' in params
            assert 'asset_type =' in query

    @pytest.mark.asyncio
    async def test_fetch_incidents_pagination(self):
        """Test limit and offset parameters"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents(limit=50, offset=100)

            query, params = mock_conn.fetch_calls[0]

            assert 50 in params
            assert 100 in params
            assert 'LIMIT' in query
            assert 'OFFSET' in query


class TestFetchIncidentsErrorHandling:
    """Test error handling and retry logic"""

    @pytest.mark.asyncio
    async def test_connection_timeout_handling(self):
        """Test asyncio.TimeoutError handled gracefully"""
        mock_conn = MockAsyncPGConnection(should_timeout=True)

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            # Should return error dict, not raise exception
            assert isinstance(result, dict)
            assert "error" in result
            assert result["error"] == "Request timeout"

    @pytest.mark.asyncio
    async def test_database_error_handling(self):
        """Test database errors return error dict"""
        mock_conn = MockAsyncPGConnection(should_error=True)

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            # Should return error dict with generic message (security)
            assert isinstance(result, dict)
            assert "error" in result
            assert result["error"] == "Database error"
            # Should NOT expose internal error details
            assert "PostgresError" not in result.get("detail", "")

    @pytest.mark.asyncio
    async def test_connection_closed_on_error(self):
        """Test connection is closed even when error occurs"""
        mock_conn = MockAsyncPGConnection(should_error=True)

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            # Connection should be closed
            assert mock_conn.closed


class TestFetchIncidentsSourceHandling:
    """Test source aggregation and formatting"""

    @pytest.mark.asyncio
    async def test_fetch_incidents_source_json_parsing(self):
        """Test sources JSON string parsed correctly"""
        import json

        mock_sources = json.dumps([
            {"source_url": "https://politi.dk/1", "source_type": "police"},
            {"source_url": "https://dr.dk/1", "source_type": "news"}
        ])

        mock_row = create_mock_row(sources=mock_sources)
        mock_conn = MockAsyncPGConnection(mock_data=[mock_row])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            # Sources should be parsed as list
            assert isinstance(result[0]["sources"], list)
            assert len(result[0]["sources"]) == 2

    @pytest.mark.asyncio
    async def test_fetch_incidents_empty_sources_handling(self):
        """Test incidents with no sources return empty array"""
        mock_row = create_mock_row(sources=None)
        mock_conn = MockAsyncPGConnection(mock_data=[mock_row])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            # Should have empty sources array, not None
            assert result[0]["sources"] == []

    @pytest.mark.asyncio
    async def test_fetch_incidents_source_fallback_names(self):
        """Test source name fallback for known domains"""
        # This tests the CASE statement in the query for source names
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            query = mock_conn.fetch_calls[0][0]

            # Should have fallback names for known domains
            assert 'politi.dk' in query
            assert 'Politiets Nyhedsliste' in query
            assert 'dr.dk' in query
            assert 'DR Nyheder' in query


class TestRunAsyncHelper:
    """Test run_async helper function"""

    def test_run_async_executes_coroutine(self):
        """Test run_async executes async coroutine in sync context"""
        async def test_coro():
            return "success"

        result = run_async(test_coro())
        assert result == "success"

    def test_run_async_handles_async_errors(self):
        """Test run_async propagates exceptions from coroutines"""
        async def error_coro():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            run_async(error_coro())

    def test_run_async_closes_event_loop(self):
        """Test run_async closes event loop after execution"""
        async def test_coro():
            return True

        # Should not raise event loop errors on multiple calls
        result1 = run_async(test_coro())
        result2 = run_async(test_coro())

        assert result1 is True
        assert result2 is True


class TestFetchIncidentsVerificationStatus:
    """Test verification status filtering"""

    @pytest.mark.asyncio
    async def test_fetch_incidents_only_verified_or_pending(self):
        """Test query only returns verified/auto_verified/pending incidents"""
        mock_conn = MockAsyncPGConnection(mock_data=[])

        with patch('db.get_connection', return_value=mock_conn):
            result = await fetch_incidents()

            query = mock_conn.fetch_calls[0][0]

            # Should filter by verification_status
            assert 'verification_status' in query
            assert 'verified' in query
            assert 'auto_verified' in query
            assert 'pending' in query
