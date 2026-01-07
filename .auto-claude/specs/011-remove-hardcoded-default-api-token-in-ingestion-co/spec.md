# Remove hardcoded default API token in ingestion config

## Overview

The `ingestion/config.py` file contains a hardcoded default value for INGEST_TOKEN: `INGEST_TOKEN = os.getenv("INGEST_TOKEN", "dw-secret-2025-nordic-drone-watch")`. If the environment variable is not set, this predictable default token will be used, allowing unauthorized access to the ingest API endpoint.

## Rationale

Hardcoded secrets are a critical security vulnerability. Anyone who reads the source code can extract this token and gain unauthorized write access to the incidents database. This could allow attackers to inject malicious or false drone incident data.

---
*This spec was created from ideation and is pending detailed specification.*
