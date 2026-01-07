# Gotchas & Pitfalls

Things to watch out for in this codebase.

## [2026-01-07 21:15]
The API endpoints (frontend/api/ingest.py, api/ingest.py) already validate that INGEST_TOKEN is set and return 500 if missing. The vulnerability is specifically in ingestion/config.py which provides a hardcoded fallback on the client/scraper side.

_Context: Security fix for hardcoded API token. Don't confuse server-side validation (which is correct) with client-side config (which has the bug)._
