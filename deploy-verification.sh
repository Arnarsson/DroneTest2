#!/bin/bash
# Deploy Verification Infrastructure
# Phase 1: Historical Incidents & Source Verification
# Date: 2025-09-30

set -e  # Exit on error

echo "========================================"
echo "DroneWatch Verification Deployment"
echo "Phase 1: Infrastructure Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ ERROR: DATABASE_URL environment variable not set${NC}"
    echo ""
    echo "Please set your DATABASE_URL:"
    echo "  export DATABASE_URL='your-postgresql-connection-string'"
    echo ""
    echo "Or run with:"
    echo "  DATABASE_URL='your-url' ./deploy-verification.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} DATABASE_URL is set"
echo ""

# Step 1: Run database migration
echo "========================================"
echo "Step 1: Running Database Migration"
echo "========================================"
echo ""
echo "This will:"
echo "  - Add verification fields to incidents table"
echo "  - Create incident_review_queue table"
echo "  - Create verification_audit table"
echo "  - Create helper views and functions"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

echo "Running migration..."
if command -v psql &> /dev/null; then
    psql "$DATABASE_URL" -f migrations/003_verification_workflow.sql
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Migration completed successfully"
    else
        echo -e "${RED}❌${NC} Migration failed"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠${NC}  psql not found. Please run the migration manually:"
    echo ""
    echo "  psql \"\$DATABASE_URL\" -f migrations/003_verification_workflow.sql"
    echo ""
    echo "Or copy the contents of migrations/003_verification_workflow.sql"
    echo "and paste into your database admin interface (e.g., Supabase SQL Editor)"
    echo ""
    read -p "Press enter when migration is complete..."
fi

echo ""

# Step 2: Update API to filter verified incidents
echo "========================================"
echo "Step 2: Updating API Code"
echo "========================================"
echo ""
echo "Updating incidents API to only show verified incidents..."
echo ""

# Backup original API file
if [ -f "frontend/api/incidents.py" ]; then
    cp frontend/api/incidents.py frontend/api/incidents.py.backup
    echo -e "${GREEN}✓${NC} Created backup: frontend/api/incidents.py.backup"
fi

# Check if already updated
if grep -q "verification_status" frontend/api/incidents.py 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  API already appears to have verification filtering"
else
    echo -e "${YELLOW}⚠${NC}  API needs manual update - see instructions below"
fi

echo ""

# Step 3: Verify the deployment
echo "========================================"
echo "Step 3: Verification Checks"
echo "========================================"
echo ""

echo "Testing database schema..."
if command -v psql &> /dev/null; then
    # Check if tables exist
    psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.incident_review_queue;" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} incident_review_queue table exists"
    else
        echo -e "${RED}❌${NC} incident_review_queue table not found"
    fi

    psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.verification_audit;" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} verification_audit table exists"
    else
        echo -e "${RED}❌${NC} verification_audit table not found"
    fi

    # Check if view exists
    psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.v_review_queue;" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} v_review_queue view exists"
    else
        echo -e "${RED}❌${NC} v_review_queue view not found"
    fi

    # Show verification stats
    echo ""
    echo "Current verification status:"
    psql "$DATABASE_URL" -c "SELECT * FROM public.v_verification_stats;"
else
    echo -e "${YELLOW}⚠${NC}  Skipping checks (psql not available)"
fi

echo ""

# Step 4: Instructions for completing deployment
echo "========================================"
echo "Step 4: Complete Deployment"
echo "========================================"
echo ""
echo -e "${GREEN}Database migration complete!${NC}"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Update Public API (frontend/api/incidents.py):"
echo "   Add this WHERE clause to the incidents query:"
echo ""
echo "   WHERE i.verification_status IN ('verified', 'auto_verified')"
echo "         AND i.status = 'active'"
echo ""
echo "2. Deploy to Production:"
echo "   - Commit changes: git add . && git commit -m 'feat: deploy verification'"
echo "   - Push to remote: git push"
echo "   - Trigger Vercel deployment (automatic on push)"
echo ""
echo "3. Set GitHub Secret (for scrapers):"
echo "   Add DATABASE_URL to GitHub Actions secrets if not already set:"
echo "   https://github.com/Arnarsson/2/settings/secrets/actions"
echo ""
echo "4. Test the System:"
echo "   - Wait for next scraper run (every 15 minutes)"
echo "   - Check logs for verification decisions"
echo "   - Police incidents should auto-verify ✓"
echo "   - Other sources should go to review queue ⚠️"
echo ""
echo "5. View Review Queue (SQL):"
echo "   SELECT * FROM public.v_review_queue;"
echo ""
echo "6. Manually Verify an Incident (SQL):"
echo "   SELECT public.complete_review("
echo "     'incident-uuid-here',"
echo "     'verify',  -- or 'reject'"
echo "     'your-name@email.com',"
echo "     'Verified with official source'"
echo "   );"
echo ""
echo "========================================"
echo "Deployment Summary"
echo "========================================"
echo ""
echo -e "${GREEN}✓${NC} Migration script: migrations/003_verification_workflow.sql"
echo -e "${GREEN}✓${NC} Verification logic: ingestion/verification.py"
echo -e "${GREEN}✓${NC} Ingester updated: ingestion/ingest.py"
echo -e "${YELLOW}⚠${NC}  API update needed: frontend/api/incidents.py"
echo ""
echo "Documentation: HISTORICAL_INCIDENTS_PLAN.md"
echo ""
echo -e "${GREEN}✅ Phase 1 deployment ready!${NC}"
echo ""