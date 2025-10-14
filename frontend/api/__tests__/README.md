# Backend API Test Suite

Comprehensive automated tests for DroneWatch 2.0 Python API endpoints.

## Quick Start

```bash
# Navigate to API directory
cd /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/frontend/api

# Create and activate virtual environment (first time only)
uv venv .venv
source .venv/bin/activate

# Install test dependencies (first time only)
uv pip install -r requirements-test.txt

# Run all tests with coverage
pytest --cov=. --cov-report=html --cov-report=term -v
```

## Current Status

- **Coverage**: 57% (Target: 40%) ✅
- **Passing Tests**: 33/59 (56%)
- **Test Files**: 3
- **Total Test Code**: ~1,400 lines

## Test Files

### 1. `test_db.py` - Database Layer Tests
- **23 tests** - All passing ✅
- **Coverage**: 80% of db.py, 100% of db_utils.py
- Tests: Connection pooling, query optimization, PostGIS operations, error handling

### 2. `test_ingest.py` - Ingestion API Tests
- **28 tests** - 10 passing (async tests) ✅
- **Coverage**: 52% of ingest.py
- Tests: Incident insertion, duplicate detection, source management, datetime parsing

### 3. `test_incidents.py` - Incidents API Tests
- **15 tests** - Need HTTP handler refactoring
- **Coverage**: 18% of incidents.py
- Tests: API endpoints, filtering, CORS, error handling

## Running Specific Tests

```bash
# Run single test file
pytest __tests__/test_db.py -v

# Run specific test class
pytest __tests__/test_db.py::TestDatabaseConnection -v

# Run specific test
pytest __tests__/test_db.py::TestDatabaseConnection::test_get_connection_supabase_pooler_detection -v

# Run with coverage for specific file
pytest __tests__/test_db.py --cov=db --cov-report=term -v
```

## Coverage Reports

### Terminal Report
```bash
pytest --cov=. --cov-report=term
```

### HTML Report
```bash
pytest --cov=. --cov-report=html
# Open: htmlcov/index.html in browser
```

### Detailed Coverage
```bash
# Show missing lines
coverage report --show-missing

# Show per-file breakdown
coverage report --omit=".venv/*,__tests__/*"
```

## Test Categories

### ✅ Fully Tested (80-100% coverage)
- Database connection management
- Query construction and optimization
- PostGIS coordinate operations
- Error handling and retries
- Source aggregation
- DateTime parsing

### ⚠️ Partially Tested (50-79% coverage)
- Incident insertion logic
- Duplicate detection
- Source deduplication
- Authentication helpers

### ⚠️ Needs Work (0-49% coverage)
- HTTP request handlers
- CORS policy enforcement
- Bearer token validation

## Dependencies

```
pytest>=7.4.0           # Test framework
pytest-asyncio>=0.21.0  # Async test support
pytest-cov>=4.1.0       # Coverage reporting
pytest-mock>=3.11.1     # Mocking utilities
httpx>=0.24.0           # HTTP testing
faker>=19.0.0           # Test data generation
asyncpg>=0.28.0         # PostgreSQL driver
```

## Configuration

### pytest.ini
- Test paths: `__tests__/`
- Coverage omits: Test files, simple utilities
- Warnings filtered for clean output

### Coverage Settings
- Source: Current directory
- Omit: `.venv/`, `__tests__/`, `simple-test.py`, `healthz.py`
- Precision: 2 decimal places
- Show missing lines: Yes

## Continuous Integration

### GitHub Actions (Recommended)
```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd frontend/api
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          cd frontend/api
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors
If you see `ImportError: attempted relative import`:
- Make sure you're in the correct directory: `frontend/api`
- Activate virtual environment: `source .venv/bin/activate`
- Reinstall dependencies: `uv pip install -r requirements-test.txt`

### Test Collection Errors
If pytest can't find tests:
- Check `pytest.ini` is present
- Verify test files start with `test_`
- Ensure test functions start with `test_`

### Coverage Issues
If coverage is 0%:
- Run with `--cov=.` not `--cov`
- Check `.coveragerc` or `pytest.ini` settings
- Ensure source files are in current directory

## Next Steps

### To Reach 70%+ Coverage
1. Fix HTTP handler mocking in `test_incidents.py` and `test_ingest.py`
2. Add integration tests with real database fixtures
3. Add performance benchmarks for query execution

### To Improve Test Quality
1. Add property-based tests with Hypothesis
2. Add mutation testing with `mutmut`
3. Add security testing with `bandit`

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- [Test Summary Report](TEST_SUMMARY.md)

---

**Last Updated**: October 14, 2025
**Test Suite Version**: 1.0.0
**Coverage**: 57%
