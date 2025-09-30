#!/bin/bash
# Cleanup unused code from old architectures

echo "🧹 Cleaning up DroneWatch codebase..."
echo

# Old architecture directories (from FastAPI/separate server days)
echo "Removing old architecture dirs..."
rm -rf api/
rm -rf server/
rm -rf worker/
rm -rf pages/
rm -rf lib/
rm -rf components/

# Temporary test/debug files
echo "Removing temporary files..."
rm -f cleanup_duplicates.py
rm -f ingest_all_historical.py
rm -f test-frontend.html
rm -f test_api.py

# Unused frontend API endpoints
echo "Removing unused API endpoints..."
rm -f frontend/api/debug.py
rm -f frontend/api/hello.py
rm -f frontend/api/test.py
rm -f frontend/api/main.py
rm -f frontend/api/index.py

# Old config/docs from previous architecture
rm -f Procfile 2>/dev/null
rm -f render.yaml 2>/dev/null

echo
echo "✅ Cleanup complete!"
echo
echo "Remaining structure:"
echo "  frontend/          - Next.js app + Vercel API routes"
echo "  frontend/api/      - 3 endpoints: incidents.py, ingest.py, db.py"
echo "  ingestion/         - GitHub Actions scraper"
echo "  .github/workflows/ - CI/CD"
echo