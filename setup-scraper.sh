#!/bin/bash
# Setup script for activating DroneWatch scraper

echo "=================================="
echo "DroneWatch Scraper Setup"
echo "=================================="
echo ""

# Define the token
INGEST_TOKEN="dw-secret-2025-nordic-drone-watch"
API_BASE_URL="https://www.dronemap.cc"

echo "Step 1: Setting GitHub Secrets..."
echo "--------------------------------"
echo ""

# Try to set GitHub secrets
echo "Setting API_BASE_URL..."
gh secret set API_BASE_URL --body "$API_BASE_URL" --repo Arnarsson/2 2>&1
if [ $? -eq 0 ]; then
    echo "✅ API_BASE_URL set successfully"
else
    echo "❌ Failed to set API_BASE_URL"
    echo ""
    echo "Please set it manually:"
    echo "1. Go to: https://github.com/Arnarsson/2/settings/secrets/actions"
    echo "2. Click 'New repository secret'"
    echo "3. Name: API_BASE_URL"
    echo "4. Value: $API_BASE_URL"
fi

echo ""
echo "Setting INGEST_TOKEN..."
gh secret set INGEST_TOKEN --body "$INGEST_TOKEN" --repo Arnarsson/2 2>&1
if [ $? -eq 0 ]; then
    echo "✅ INGEST_TOKEN set successfully"
else
    echo "❌ Failed to set INGEST_TOKEN"
    echo ""
    echo "Please set it manually:"
    echo "1. Go to: https://github.com/Arnarsson/2/settings/secrets/actions"
    echo "2. Click 'New repository secret'"
    echo "3. Name: INGEST_TOKEN"
    echo "4. Value: $INGEST_TOKEN"
fi

echo ""
echo "=================================="
echo "Step 2: Vercel Environment Variable"
echo "=================================="
echo ""
echo "⚠️  You MUST also add INGEST_TOKEN to Vercel:"
echo ""
echo "1. Go to: https://vercel.com/arnarssons-projects/dronewatchv2/settings/environment-variables"
echo "2. Add new variable:"
echo "   Name: INGEST_TOKEN"
echo "   Value: $INGEST_TOKEN"
echo "   Environment: Production, Preview, Development"
echo "3. Click Save"
echo "4. Redeploy (or wait for next deployment)"
echo ""

echo "=================================="
echo "Step 3: Test the Scraper"
echo "=================================="
echo ""
echo "Option A - Trigger via GitHub Actions:"
echo "  gh workflow run 193622201 --repo Arnarsson/2"
echo ""
echo "Option B - View at:"
echo "  https://github.com/Arnarsson/2/actions/workflows/ingest.yml"
echo ""
echo "=================================="
echo "Setup Summary"
echo "=================================="
echo "Token to use: $INGEST_TOKEN"
echo "API URL: $API_BASE_URL"
echo ""
echo "After setup, the scraper will:"
echo "- Run automatically every 15 minutes"
echo "- Scrape Danish police RSS feeds"
echo "- Scrape DR and TV2 news"
echo "- Ingest incidents into your database"
echo ""
echo "✅ Script complete!"