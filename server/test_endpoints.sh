#!/bin/bash

# Quick endpoint smoke tests for DroneWatch API
# Usage: ./test_endpoints.sh

API_BASE="${API_BASE:-http://localhost:8000}"
INGEST_TOKEN="${INGEST_TOKEN:-your-secret-token-here}"

echo "🔍 Testing DroneWatch API at: $API_BASE"
echo "================================"

# Health check
echo -e "\n1. Health Check:"
curl -s "$API_BASE/healthz" | jq '.'

# List incidents
echo -e "\n2. List Incidents (evidence ≥2, DK):"
curl -s "$API_BASE/incidents?min_evidence=2&country=DK&limit=3" | jq '.[] | {id, title, evidence_score, lat, lon}'

# Pagination test
echo -e "\n3. Pagination Test (offset=0, limit=2):"
curl -s "$API_BASE/incidents?limit=2&offset=0" | jq 'length'

# BBox query (Denmark)
echo -e "\n4. BBox Query (Denmark: 7.7,54.4,15.5,57.8):"
curl -s "$API_BASE/incidents?bbox=7.7,54.4,15.5,57.8&min_evidence=2" | jq 'length'

# Invalid BBox (should fail)
echo -e "\n5. Invalid BBox Test (should return 400):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" "$API_BASE/incidents?bbox=invalid"

# Embed snippet
echo -e "\n6. Embed Snippet:"
curl -s "$API_BASE/embed/snippet?min_evidence=3&country=DK&height=600" | head -3

# Ingest without token (should fail)
echo -e "\n7. Ingest without token (should return 401):"
curl -s -X POST "$API_BASE/ingest" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}' \
  -o /dev/null -w "HTTP Status: %{http_code}\n"

# Ingest with valid token
echo -e "\n8. Ingest with valid token:"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
curl -s -X POST "$API_BASE/ingest" \
  -H "Authorization: Bearer $INGEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test: Drone sighting at $(date +%H:%M)\",
    \"narrative\": \"Automated test incident\",
    \"occurred_at\": \"$TIMESTAMP\",
    \"lat\": 55.6761,
    \"lon\": 12.5683,
    \"asset_type\": \"airport\",
    \"status\": \"active\",
    \"evidence_score\": 2,
    \"country\": \"DK\",
    \"sources\": [{
      \"source_url\": \"https://example.com/test\",
      \"source_type\": \"media\",
      \"source_quote\": \"Test quote\"
    }]
  }" | jq '.'

echo -e "\n✅ All tests completed!"