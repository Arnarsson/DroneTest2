#!/bin/bash
# Deploy AI-Powered Duplicate Detection Migrations to Supabase
# Run this script from your local machine (not in Claude Code environment)

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== DroneWatch Duplicate Detection Migration Deployment ===${NC}\n"

# Database URL (use port 5432 for migrations, NOT 6543)
export DATABASE_URL="postgresql://postgres.uhwsuaebakkdmdogzrrz:4LR3qjEQEa0WAWut@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

echo -e "${YELLOW}Step 1: Checking database connection...${NC}"
if psql "$DATABASE_URL" -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database connection successful${NC}\n"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    echo "Please check your DATABASE_URL and network connection"
    exit 1
fi

echo -e "${YELLOW}Step 2: Checking current migration status...${NC}"
psql "$DATABASE_URL" -c "SELECT version, description, executed_at FROM public.schema_migrations ORDER BY version DESC LIMIT 5;" 2>/dev/null || echo "Migration tracking table doesn't exist yet (ok)"
echo ""

echo -e "${YELLOW}Step 3: Checking pgvector extension availability...${NC}"
PGVECTOR_AVAILABLE=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'vector';" 2>/dev/null | tr -d ' ')

if [ "$PGVECTOR_AVAILABLE" = "1" ]; then
    echo -e "${GREEN}✓ pgvector extension is available${NC}"

    # Check if already enabled
    PGVECTOR_ENABLED=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector';" 2>/dev/null | tr -d ' ')

    if [ "$PGVECTOR_ENABLED" = "1" ]; then
        echo -e "${GREEN}✓ pgvector extension is already enabled${NC}\n"
    else
        echo -e "${YELLOW}→ Enabling pgvector extension...${NC}"
        psql "$DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS vector;" || {
            echo -e "${RED}✗ Failed to enable pgvector${NC}"
            echo "Please enable it manually in Supabase dashboard:"
            echo "  1. Go to Database → Extensions"
            echo "  2. Search for 'pgvector'"
            echo "  3. Click Enable"
            exit 1
        }
        echo -e "${GREEN}✓ pgvector extension enabled${NC}\n"
    fi
else
    echo -e "${RED}✗ pgvector extension is NOT available${NC}"
    echo ""
    echo "MANUAL ACTION REQUIRED:"
    echo "1. Go to your Supabase dashboard: https://supabase.com/dashboard"
    echo "2. Select your project"
    echo "3. Navigate to: Database → Extensions"
    echo "4. Search for 'pgvector'"
    echo "5. Click 'Enable' next to pgvector"
    echo "6. Wait 30-60 seconds for activation"
    echo "7. Re-run this script"
    echo ""
    exit 1
fi

echo -e "${YELLOW}Step 4: Deploying Migration 020 (Enhanced Content Hash)...${NC}"
if psql "$DATABASE_URL" -f migrations/020_enhanced_content_hash.sql; then
    echo -e "${GREEN}✓ Migration 020 deployed successfully${NC}\n"
else
    echo -e "${RED}✗ Migration 020 failed${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 5: Verifying Migration 020...${NC}"
CONTENT_HASH_EXISTS=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'incidents' AND column_name = 'content_hash';" | tr -d ' ')
if [ "$CONTENT_HASH_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ content_hash column exists${NC}"
else
    echo -e "${RED}✗ content_hash column NOT found${NC}"
    exit 1
fi

CONSTRAINT_EXISTS=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM pg_constraint WHERE conname = 'incidents_content_hash_unique';" | tr -d ' ')
if [ "$CONSTRAINT_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ Unique constraint exists${NC}\n"
else
    echo -e "${RED}✗ Unique constraint NOT found${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 6: Deploying Migration 021 (Vector Embeddings)...${NC}"
if psql "$DATABASE_URL" -f migrations/021_vector_embeddings.sql; then
    echo -e "${GREEN}✓ Migration 021 deployed successfully${NC}\n"
else
    echo -e "${RED}✗ Migration 021 failed${NC}"
    echo "This usually means pgvector is not enabled properly"
    exit 1
fi

echo -e "${YELLOW}Step 7: Verifying Migration 021...${NC}"
EMBEDDINGS_TABLE_EXISTS=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'incident_embeddings';" | tr -d ' ')
if [ "$EMBEDDINGS_TABLE_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ incident_embeddings table exists${NC}"
else
    echo -e "${RED}✗ incident_embeddings table NOT found${NC}"
    exit 1
fi

FUNCTION_EXISTS=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM pg_proc WHERE proname = 'find_similar_incidents';" | tr -d ' ')
if [ "$FUNCTION_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ find_similar_incidents function exists${NC}\n"
else
    echo -e "${RED}✗ find_similar_incidents function NOT found${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 8: Deploying Migration 022 (User Feedback System)...${NC}"
if psql "$DATABASE_URL" -f migrations/022_duplicate_feedback.sql; then
    echo -e "${GREEN}✓ Migration 022 deployed successfully${NC}\n"
else
    echo -e "${RED}✗ Migration 022 failed${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 9: Verifying Migration 022...${NC}"
FEEDBACK_TABLE_EXISTS=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'duplicate_feedback';" | tr -d ' ')
if [ "$FEEDBACK_TABLE_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ duplicate_feedback table exists${NC}"
else
    echo -e "${RED}✗ duplicate_feedback table NOT found${NC}"
    exit 1
fi

VIEW_EXISTS=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.views WHERE table_name = 'duplicate_feedback_analysis';" | tr -d ' ')
if [ "$VIEW_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ duplicate_feedback_analysis view exists${NC}\n"
else
    echo -e "${RED}✗ duplicate_feedback_analysis view NOT found${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 10: Testing duplicate detection...${NC}"
echo "Testing content_hash generation on existing incidents..."
HASHED_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM incidents WHERE content_hash IS NOT NULL;" | tr -d ' ')
TOTAL_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM incidents;" | tr -d ' ')

echo -e "${GREEN}✓ ${HASHED_COUNT}/${TOTAL_COUNT} incidents have content_hash${NC}"

if [ "$HASHED_COUNT" = "$TOTAL_COUNT" ]; then
    echo -e "${GREEN}✓ All incidents have content_hash (100%)${NC}\n"
else
    echo -e "${YELLOW}→ Some incidents missing content_hash (trigger will auto-generate on next update)${NC}\n"
fi

echo -e "${YELLOW}Step 11: Updating migration tracking (if table exists)...${NC}"
if psql "$DATABASE_URL" -c "SELECT 1 FROM schema_migrations LIMIT 1;" > /dev/null 2>&1; then
    psql "$DATABASE_URL" -c "
    INSERT INTO public.schema_migrations (version, description, executed_by)
    VALUES
      ('020', 'Enhanced content hash for duplicate detection', 'manual-deployment'),
      ('021', 'Vector embeddings for semantic similarity', 'manual-deployment'),
      ('022', 'User feedback system for continuous learning', 'manual-deployment')
    ON CONFLICT (version) DO NOTHING;
    " > /dev/null 2>&1
    echo -e "${GREEN}✓ Migration tracking updated${NC}\n"
else
    echo -e "${YELLOW}→ Migration tracking table doesn't exist (skipping)${NC}\n"
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  ✓ ALL MIGRATIONS DEPLOYED SUCCESSFULLY!                   ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Summary:${NC}"
echo "  ✓ Migration 020: Enhanced Content Hash"
echo "  ✓ Migration 021: Vector Embeddings (pgvector)"
echo "  ✓ Migration 022: User Feedback System"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "  1. Deploy updated code to Vercel (git push origin main)"
echo "  2. Monitor duplicate detection in Vercel logs"
echo "  3. Run: python3 ingestion/duplicate_detection_stats.py"
echo "  4. Check for 'Tier 1', 'Tier 2', 'Tier 3' log messages"
echo ""
echo -e "${GREEN}The 3-tier duplicate detection system is now ACTIVE! 🎉${NC}"
echo ""
