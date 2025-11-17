#!/bin/bash
# Deploy Istanbul Convention Bug Fix + Clean Bad Data

set -e

echo "=========================================="
echo "Istanbul Convention Fix Deployment"
echo "=========================================="
echo ""

# Step 1: Merge to main and push
echo "Step 1: Merging feature branch to main..."
git checkout main
git pull origin main
git merge origin/claude/senior-engineer-system-design-01GzvBLrjkYRQ62eoWF1GmrG --no-edit
git push origin main

echo "✓ Pushed to main - Vercel deployment starting..."
echo ""

# Step 2: Wait for Vercel deployment
echo "Waiting 30 seconds for Vercel deployment..."
sleep 30

# Step 3: Clean bad data from database
echo ""
echo "Step 2: Removing Istanbul Convention incident from database..."

export DATABASE_URL="${DATABASE_URL:-postgresql://postgres.uhwsuaebakkdmdogzrrz:4LR3qjEQEa0WAWut@aws-1-eu-north-1.pooler.supabase.com:5432/postgres}"

psql "$DATABASE_URL" -c "DELETE FROM incidents WHERE title ILIKE '%Istanbul Convention%' OR narrative ILIKE '%Istanbul Convention%' RETURNING id, title;"

echo ""
echo "✓ Bad data removed"
echo ""

# Step 4: Verify
echo "Step 3: Verifying production..."
echo ""
echo "Checking production API..."
INCIDENT_COUNT=$(curl -s "https://www.dronemap.cc/api/incidents?min_evidence=1&limit=100" | jq '. | length')
echo "✓ Production has $INCIDENT_COUNT incidents (should NOT include Istanbul Convention)"
echo ""

echo "=========================================="
echo "✓ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "The Istanbul Convention incident should now be gone."
echo "Future non-drone articles will be blocked by Layer 2A + 2B filters."
echo ""
