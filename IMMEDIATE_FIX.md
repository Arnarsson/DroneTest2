# 🚨 IMMEDIATE FIX - Vercel Showing "Error loading incidents"

**Issue**: Vercel can't connect to PostgreSQL at 135.181.101.70:5432 (authentication failing)

**Solution**: Use production API temporarily OR fix PostgreSQL auth

---

## 🔧 QUICK FIX (2 minutes) - Use Production API

This will get your site working immediately while we fix the PostgreSQL issue:

### Go to Vercel Environment Variables:
https://vercel.com/arnarssons-projects/drone-test22/settings/environment-variables

### Option A: Point to Production (Fastest)

1. **Find** `DATABASE_URL` and **DELETE IT** (or set to empty)

2. **Add** new variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://www.dronemap.cc/api`
   - Environments: All 3

3. **Redeploy**

This makes drone-test22 use dronemap.cc's API (which works and has data).

---

## 🔍 ROOT CAUSE

Your local Supabase PostgreSQL is rejecting connections with:
```
❌ Authentication failed! Check password.
```

**Current DATABASE_URL**:
```
postgresql://postgres:El54d9tlwzgmn7EH18K1vLfVXjKg5CCA@135.181.101.70:5432/postgres
```

The password `El54d9tlwzgmn7EH18K1vLfVXjKg5CCA` is being rejected.

**Possible reasons:**
1. This password is for **internal Docker** use only (not external)
2. PostgreSQL has different credentials for external connections
3. PostgreSQL `pg_hba.conf` not configured for external MD5 auth

---

## 🛠️ PERMANENT FIX - Fix PostgreSQL Auth

### Check your server's PostgreSQL configuration:

```bash
# SSH into 135.181.101.70
ssh user@135.181.101.70

# Check if postgres user has a password
sudo -u postgres psql -c "SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname='postgres';"

# Try to connect locally
psql -U postgres -h 135.181.101.70 -d postgres
# Enter password when prompted

# Check pg_hba.conf
sudo cat /var/lib/postgresql/data/pg_hba.conf | grep -v "^#"
```

### What to look for:

**In `pg_hba.conf`, you need:**
```
host    all             all             0.0.0.0/0               md5
```

**NOT:**
```
host    all             all             0.0.0.0/0               trust   # Too permissive
host    all             all             127.0.0.1/32            md5     # Only localhost
```

### If using Docker Supabase:

The password might be set in `docker-compose.yml`:

```bash
# Check Docker compose file
cat docker-compose.yml | grep POSTGRES_PASSWORD
```

The actual password might be **different** from the one in your .env file.

---

## 🎯 RECOMMENDED APPROACH

**Right now:**
1. Use production API (Option A above) to unblock
2. Your site will work with dronemap.cc's data

**Then investigate:**
1. Find the correct PostgreSQL password
2. Or configure PostgreSQL to accept your password
3. Update Vercel DATABASE_URL with correct credentials
4. Redeploy to use local Supabase

---

## ✅ VERIFICATION

After applying Option A (production API):

```bash
curl "https://drone-test22.vercel.app/api/incidents?limit=3"
```

Should return incidents from dronemap.cc (not empty array).

The map should load without "Error loading incidents".

---

**Choose your path:**
- 🏃 **Fast**: Use production API now (2 min)
- 🔧 **Proper**: Fix PostgreSQL auth (15-30 min)
- 🤝 **Both**: Use production now, fix PostgreSQL later

---

**Updated**: October 6, 2025
**Priority**: 🔴 CRITICAL
