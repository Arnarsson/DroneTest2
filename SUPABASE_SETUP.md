# 🚀 DroneWatch Supabase Setup Guide

Your Supabase project is configured and ready! Follow these steps to get DroneWatch running.

## 📋 Project Details

- **Project Name**: dronewatch
- **Project ID**: uhwsuaebakkdmdogzrrz
- **URL**: https://uhwsuaebakkdmdogzrrz.supabase.co
- **Region**: US East 1

## 🔐 Security Keys

**⚠️ IMPORTANT: Keep these secure!**

- **Anon Key** (public, for frontend):
  ```
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...mxolo
  ```
  ✅ Safe to use in browser/frontend

- **Service Role Key** (secret, for backend ONLY):
  ```
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...qEZlE
  ```
  ❌ NEVER expose in frontend code!

## 🛠️ Step 1: Database Setup

### 1.1 Enable PostGIS
Go to [Supabase SQL Editor](https://supabase.com/dashboard/project/uhwsuaebakkdmdogzrrz/sql/new) and run:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 1.2 Create Schema
Run the entire contents of `/sql/supabase_schema.sql` in the SQL Editor.

### 1.3 (Optional) Add Demo Data
Run `/sql/seed_demo.sql` for test incidents.

### 1.4 Verify Setup
```sql
-- Check PostGIS
SELECT PostGIS_version();

-- Check tables exist
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('incidents', 'sources', 'assets');

-- Verify RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;
```

## 🖥️ Step 2: Backend Setup

### 2.1 Environment Configuration
The `.env` file is already configured with your credentials:

```bash
cd server
# .env already contains your Supabase credentials
```

### 2.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.3 Test Database Connection
```bash
python test_db_connection.py
# Should show: ✅ Connected to PostgreSQL
```

### 2.4 Run the API
```bash
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API docs.

## 🎨 Step 3: Frontend Configuration

### 3.1 Update Frontend Environment
Create `.env.local` in your frontend directory:

```env
# For Next.js
NEXT_PUBLIC_SUPABASE_URL=https://uhwsuaebakkdmdogzrrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVod3N1YWViYWtrZG1kb2d6cnJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNTIxNTAsImV4cCI6MjA3NDcyODE1MH0.mOZJHXepmoRjiFYVqrik2tpLJ4Y-hE-z5GMQR3mxolo
NEXT_PUBLIC_API_URL=http://localhost:8000

# For Vite
VITE_SUPABASE_URL=https://uhwsuaebakkdmdogzrrz.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVod3N1YWViYWtrZG1kb2d6cnJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNTIxNTAsImV4cCI6MjA3NDcyODE1MH0.mOZJHXepmoRjiFYVqrik2tpLJ4Y-hE-z5GMQR3mxolo
VITE_API_URL=http://localhost:8000
```

### 3.2 Frontend API Integration

#### Option A: Via FastAPI Backend
```javascript
// Recommended: Use your FastAPI backend
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const response = await fetch(`${API_URL}/incidents?min_evidence=2`);
const incidents = await response.json();
```

#### Option B: Direct Supabase (Read-Only)
```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

// Read incidents directly (anon has SELECT permission)
const { data, error } = await supabase
  .from('incidents')
  .select('*')
  .gte('evidence_score', 2)
  .order('occurred_at', { ascending: false });
```

## 🧪 Step 4: Test Everything

### 4.1 Test API Health
```bash
curl http://localhost:8000/healthz
# Should return: {"ok": true, "service": "dronewatch-api"}
```

### 4.2 Test Incidents Endpoint
```bash
curl "http://localhost:8000/incidents?min_evidence=2&country=DK"
# Should return incidents array (empty initially)
```

### 4.3 Test Ingestion
```bash
export INGEST_TOKEN="dw-secret-2025-nordic-drone-watch"

curl -X POST http://localhost:8000/ingest \
  -H "Authorization: Bearer $INGEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test: Drone at Copenhagen Airport",
    "narrative": "Testing the ingestion pipeline",
    "occurred_at": "2025-09-29T12:00:00Z",
    "lat": 55.6180,
    "lon": 12.6476,
    "asset_type": "airport",
    "status": "active",
    "evidence_score": 3,
    "country": "DK",
    "sources": [{
      "source_url": "https://politi.dk/test",
      "source_type": "police",
      "source_quote": "Test quote from police"
    }]
  }'
```

### 4.4 Verify in Supabase Dashboard
Go to [Table Editor](https://supabase.com/dashboard/project/uhwsuaebakkdmdogzrrz/editor) and check the `incidents` table.

## 🔧 n8n Integration

Use these settings in your n8n HTTP Request node:

- **URL**: `https://your-api-domain.com/ingest`
- **Method**: POST
- **Headers**:
  ```
  Authorization: Bearer dw-secret-2025-nordic-drone-watch
  Content-Type: application/json
  ```
- **Body**: JSON matching the `/ingest` schema

## 📦 Deployment

### Deploy API (Railway/Render/Fly.io)
```bash
# Set environment variables on your platform:
DATABASE_URL=postgresql+asyncpg://...
INGEST_TOKEN=your-secure-token
ALLOWED_ORIGINS=https://dronewatch.cc
ENV=production
```

### Deploy Frontend (Vercel)
```bash
# Set environment variables in Vercel:
NEXT_PUBLIC_SUPABASE_URL=https://uhwsuaebakkdmdogzrrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...mxolo
NEXT_PUBLIC_API_URL=https://api.dronewatch.cc
```

## 🚨 Security Checklist

- [ ] ✅ Service role key ONLY in backend `.env`
- [ ] ✅ RLS enabled on all tables
- [ ] ✅ Anon has SELECT-only permissions
- [ ] ✅ INGEST_TOKEN is secure and unique
- [ ] ✅ CORS limited to your domains
- [ ] ✅ HTTPS in production

## 📞 Need Help?

1. Check [Supabase Dashboard](https://supabase.com/dashboard/project/uhwsuaebakkdmdogzrrz)
2. View [API Logs](https://supabase.com/dashboard/project/uhwsuaebakkdmdogzrrz/logs/explorer)
3. Test with `test_db_connection.py`
4. Run `test_endpoints.sh` for API validation

Your DroneWatch backend is now connected to Supabase! 🎉