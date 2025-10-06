# 🔴 Supabase PostgreSQL Connection Issue

**Date**: October 6, 2025
**Status**: ❌ Cannot connect to PostgreSQL

---

## 🎯 Problem Summary

The self-hosted Supabase instance at **135.181.101.70** is not accepting external PostgreSQL connections. Environment files have been configured, but connection tests fail.

---

## ✅ What Was Configured

### 1. `/root/repo/.env.local` (Frontend/API)
```bash
DATABASE_URL=postgresql://postgres:El54d9tlwzgmn7EH18K1vLfVXjKg5CCA@135.181.101.70:5432/postgres
SUPABASE_URL=http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io
SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
SUPABASE_SERVICE_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
INGEST_TOKEN=dw-secret-2025-nordic-drone-watch
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

### 2. `/root/repo/ingestion/.env` (Scraper)
```bash
DATABASE_URL=postgresql://postgres:El54d9tlwzgmn7EH18K1vLfVXjKg5CCA@135.181.101.70:5432/postgres
API_BASE_URL=http://localhost:3000/api
INGEST_TOKEN=dw-secret-2025-nordic-drone-watch
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Your OpenAI API key
```

---

## ❌ Test Results

### PostgreSQL Direct Connection: FAILED ❌

Tested 4 different PostgreSQL connection configurations:

| Configuration | Port | Result | Issue |
|--------------|------|--------|-------|
| `postgres` user | 5432 | ❌ Failed | Authentication failed |
| `postgres` user | 6543 | ⏱️ Timeout | Port not exposed |
| `supabase` user | 5432 | ❌ Failed | Authentication failed |
| `postgres` user | 54322 | ⏱️ Timeout | Port not exposed |

**Test command used:**
```bash
python3 test_all_connections.py
```

### ✅ REST API: WORKING!

**Good news:** The Supabase REST API (PostgREST) via Kong gateway **IS accessible**:

```bash
# Test successful:
curl "http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io/rest/v1/"
# Returns: OpenAPI schema with incidents, sources, incident_sources tables ✅

# Data query works:
curl "http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io/rest/v1/incidents" \
  -H "apikey: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
# Returns: [] (empty database, but accessible) ✅
```

**Confirmed:**
- ✅ Kong gateway responding at port 8000
- ✅ PostgREST API accessible at `/rest/v1/`
- ✅ Database schema exists (incidents, sources, incident_sources tables)
- ✅ PostGIS installed and working
- ✅ Authentication working with ANON_KEY

---

## 🔍 Root Cause Analysis

### Issue 1: PostgreSQL Ports Not Exposed
Port 5432 accepts connections but rejects authentication. Ports 6543 and 54322 timeout, indicating they're not exposed externally.

### Issue 2: Authentication Failure
The password `El54d9tlwzgmn7EH18K1vLfVXjKg5CCA` (from `SERVICE_PASSWORD_POSTGRES`) is being rejected.

### Issue 3: Docker Internal Networking
Your `.env` shows:
```bash
POSTGRES_HOSTNAME=supabase-db  # Internal Docker hostname
POSTGRES_PORT=5432              # Internal Docker port
```

This suggests PostgreSQL is running in a Docker network and may not be properly exposed externally.

---

## 🛠️ Required Actions

### Option A: Expose PostgreSQL Port Externally (Recommended)

**1. Check your `docker-compose.yml`** for the Supabase database service:
```yaml
services:
  db:
    image: supabase/postgres:...
    ports:
      - "5432:5432"  # ← This line exposes PostgreSQL externally
```

**2. If the port mapping is missing, add it:**
```yaml
services:
  db:
    ports:
      - "5432:5432"  # Expose PostgreSQL
```

**3. Restart the Supabase stack:**
```bash
docker-compose down
docker-compose up -d
```

**4. Verify the password** in your `docker-compose.yml` or `.env`:
```bash
POSTGRES_PASSWORD=El54d9tlwzgmn7EH18K1vLfVXjKg5CCA
```

**5. Check PostgreSQL is listening on all interfaces:**
```bash
docker exec <db-container-name> psql -U postgres -c "SHOW listen_addresses"
# Should return: listen_addresses = '*'
```

---

### Option B: Use PostgREST API Instead (Alternative)

If you cannot expose PostgreSQL directly, you can use the Supabase REST API through Kong:

**1. Update connection code** to use PostgREST instead of asyncpg
**2. Use the Kong gateway URL:** `http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io`
**3. Use service role key for authentication**

**Note:** This requires significant code changes in `/root/repo/frontend/api/db.py`.

---

### Option C: SSH Tunnel (Temporary Workaround)

Create an SSH tunnel to the server:
```bash
ssh -L 5432:localhost:5432 user@135.181.101.70
```

Then connect to `localhost:5432` instead of `135.181.101.70:5432`.

---

## 🎯 Next Steps

**For you to do:**

1. **Check Docker Compose configuration** on the server at `135.181.101.70`
   ```bash
   ssh user@135.181.101.70
   cat docker-compose.yml | grep -A 10 "db:" | grep -i "ports"
   ```

2. **Verify PostgreSQL password** matches:
   ```bash
   docker exec <supabase-db-container> psql -U postgres -c "SELECT 1"
   # Use password: El54d9tlwzgmn7EH18K1vLfVXjKg5CCA
   ```

3. **Check firewall rules**:
   ```bash
   sudo ufw status | grep 5432
   # Or if using iptables:
   sudo iptables -L -n | grep 5432
   ```

4. **Once PostgreSQL is accessible**, re-run the test:
   ```bash
   cd /root/repo
   python3 test_all_connections.py
   ```

5. **Update `.env` files** if a different port/user is needed

---

## 📋 Files Created

- ✅ `/root/repo/.env.local` - Frontend environment config
- ✅ `/root/repo/ingestion/.env` - Scraper environment config
- 🔧 `/root/repo/test_connection.py` - Simple connection test
- 🔧 `/root/repo/test_all_connections.py` - Comprehensive test suite
- 📝 `/root/repo/SUPABASE_CONNECTION_ISSUE.md` - This document

---

## 🤔 Questions to Answer

1. **Is the Supabase instance running on the same machine as DroneWatch?**
   - If yes: Use `localhost` or Docker network
   - If no: Need external port exposure

2. **What is the correct PostgreSQL username?**
   - Default Supabase: `postgres`
   - Custom setup: Check your configuration

3. **What ports are exposed on 135.181.101.70?**
   ```bash
   nmap -p 5432,6543,54322 135.181.101.70
   ```

---

## 📚 Reference

**Your Supabase Configuration:**
- Kong Gateway: `http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io`
- Internal DB Host: `supabase-db` (Docker)
- Internal DB Port: `5432`
- Database Name: `postgres`
- Password: `El54d9tlwzgmn7EH18K1vLfVXjKg5CCA`

**DroneWatch Requirements:**
- Direct PostgreSQL connection for `asyncpg` library
- Used by: Frontend API (`/api/incidents.py`) and Scraper (`ingestion/`)
- Alternative: Rewrite to use PostgREST API

---

**Last Updated**: October 6, 2025
**Status**: ⏳ Waiting for server configuration
