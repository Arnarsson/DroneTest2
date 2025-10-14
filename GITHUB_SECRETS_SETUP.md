# GitHub Secrets Setup - URGENT FIX REQUIRED

## Current Issue

GitHub Actions workflow is **failing to ingest incidents** because required secrets are not configured.

**Error**: `Invalid URL '/ingest': No scheme supplied. Perhaps you meant https:///ingest?`

## Required Secrets

Navigate to: **Settings → Secrets and variables → Actions → New repository secret**

Add the following 4 secrets:

### 1. API_BASE_URL
```
https://www.dronemap.cc
```
**Purpose**: Base URL for API ingestion endpoint

### 2. INGEST_TOKEN
```
<YOUR_SECRET_INGEST_TOKEN>
```
**Purpose**: Bearer token for authenticating scraper requests
**Location**: Check Vercel environment variables or `.env.production`

### 3. DATABASE_URL
```
<YOUR_SUPABASE_CONNECTION_STRING>
```
**Purpose**: Direct database connection for ingestion
**Format**: `postgresql://user:password@host:5432/postgres`
**Note**: Use port 5432 (direct connection), NOT 6543 (pooler)

### 4. OPENROUTER_API_KEY (Optional but Recommended)
```
sk-or-v1-...
```
**Purpose**: AI-powered location extraction and incident verification
**Without**: Falls back to regex pattern matching (less accurate)

## How to Add Secrets

```bash
# Method 1: Using GitHub CLI (recommended)
gh secret set API_BASE_URL --body "https://www.dronemap.cc"
gh secret set INGEST_TOKEN --body "<YOUR_TOKEN>"
gh secret set DATABASE_URL --body "<YOUR_DATABASE_URL>"
gh secret set OPENROUTER_API_KEY --body "<YOUR_API_KEY>"

# Method 2: Using GitHub UI
1. Go to: https://github.com/Arnarsson/DroneWatch2.0/settings/secrets/actions
2. Click "New repository secret"
3. Enter name and value
4. Click "Add secret"
```

## Verify Secrets Are Set

```bash
gh secret list --repo Arnarsson/DroneWatch2.0
```

Expected output:
```
API_BASE_URL            2025-10-14T...
CLAUDE_CODE_OAUTH_TOKEN 2025-10-14T...
DATABASE_URL            2025-10-14T...
INGEST_TOKEN            2025-10-14T...
OPENROUTER_API_KEY      2025-10-14T...
```

## Test After Setup

Once secrets are configured:

1. **Wait for next scheduled run** (every 5 minutes)
   ```bash
   gh run watch
   ```

2. **OR trigger manually**:
   ```bash
   gh workflow run ingest.yml
   ```

3. **Check success**:
   ```bash
   gh run list --limit 1
   ```
   Should show: `completed  success  DroneWatch Data Ingestion`

4. **Verify incidents ingested**:
   ```bash
   curl -s "https://www.dronemap.cc/api/incidents?limit=500" | jq 'length'
   ```
   Should show: > 8 (currently only 8 Danish incidents)

## Impact

**Before fix**:
- ❌ GitHub Actions failing every 5 minutes
- ❌ No new incidents ingested since deployment
- ❌ European expansion blocked

**After fix**:
- ✅ Automated ingestion every 5 minutes
- ✅ European incidents start appearing
- ✅ 50-100 total incidents expected

## Priority

🔴 **CRITICAL** - European expansion feature is blocked without these secrets

---

**Created**: 2025-10-14 19:30 UTC
**Status**: Waiting for user to add secrets
