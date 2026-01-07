#!/bin/bash
# Setup script for activating DroneWatch scraper

set -e

MIN_TOKEN_LENGTH=16
API_BASE_URL="https://www.dronemap.cc"

# Function to display token generation guidance
show_token_guidance() {
    echo ""
    echo "How to generate a secure token:"
    echo "--------------------------------"
    echo "Option 1 - Using openssl (recommended):"
    echo "  openssl rand -base64 32"
    echo ""
    echo "Option 2 - Using /dev/urandom:"
    echo "  head -c 32 /dev/urandom | base64 | tr -d '\\n'"
    echo ""
    echo "Option 3 - Using Python:"
    echo "  python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
    echo ""
}

# Function to validate token
validate_token() {
    local token="$1"

    if [ -z "$token" ]; then
        echo "Error: Token cannot be empty."
        return 1
    fi

    if [ ${#token} -lt $MIN_TOKEN_LENGTH ]; then
        echo "Error: Token must be at least $MIN_TOKEN_LENGTH characters long."
        echo "       Your token is ${#token} characters."
        return 1
    fi

    # Warn if token looks like a placeholder
    if [[ "$token" == *"your-"* ]] || [[ "$token" == *"placeholder"* ]] || [[ "$token" == *"example"* ]]; then
        echo "Warning: Token appears to be a placeholder. Please use a real secure token."
        return 1
    fi

    return 0
}

echo "=================================="
echo "DroneWatch Scraper Setup"
echo "=================================="
echo ""

# Get token from: 1) Command line argument, 2) Environment variable, 3) Interactive prompt
if [ -n "$1" ]; then
    INGEST_TOKEN="$1"
    echo "Using token from command line argument."
elif [ -n "$INGEST_TOKEN" ]; then
    echo "Using token from INGEST_TOKEN environment variable."
else
    echo "No token provided via argument or environment variable."
    echo ""
    show_token_guidance
    echo ""
    echo "Usage:"
    echo "  ./setup-scraper.sh <your-secure-token>"
    echo "  # OR"
    echo "  export INGEST_TOKEN=<your-secure-token>"
    echo "  ./setup-scraper.sh"
    echo ""

    # Interactive prompt
    read -p "Enter your INGEST_TOKEN (or press Ctrl+C to exit): " INGEST_TOKEN
fi

echo ""

# Validate the token
if ! validate_token "$INGEST_TOKEN"; then
    echo ""
    show_token_guidance
    exit 1
fi

echo "Token validated successfully (length: ${#INGEST_TOKEN} characters)."
echo ""

echo "Step 1: Setting GitHub Secrets..."
echo "--------------------------------"
echo ""

# Try to set GitHub secrets
echo "Setting API_BASE_URL..."
gh secret set API_BASE_URL --body "$API_BASE_URL" --repo Arnarsson/2 2>&1
if [ $? -eq 0 ]; then
    echo "API_BASE_URL set successfully"
else
    echo "Failed to set API_BASE_URL"
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
    echo "INGEST_TOKEN set successfully"
else
    echo "Failed to set INGEST_TOKEN"
    echo ""
    echo "Please set it manually:"
    echo "1. Go to: https://github.com/Arnarsson/2/settings/secrets/actions"
    echo "2. Click 'New repository secret'"
    echo "3. Name: INGEST_TOKEN"
    echo "4. Value: <your-token>"
fi

echo ""
echo "=================================="
echo "Step 2: Vercel Environment Variable"
echo "=================================="
echo ""
echo "You MUST also add INGEST_TOKEN to Vercel:"
echo ""
echo "1. Go to: https://vercel.com/arnarssons-projects/dronewatchv2/settings/environment-variables"
echo "2. Add new variable:"
echo "   Name: INGEST_TOKEN"
echo "   Value: <use the same token you provided above>"
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
echo "Token: [REDACTED - ${#INGEST_TOKEN} characters]"
echo "API URL: $API_BASE_URL"
echo ""
echo "IMPORTANT: Make sure to use the SAME token in:"
echo "  - GitHub Secrets (set above)"
echo "  - Vercel Environment Variables"
echo "  - Local .env file (if running locally)"
echo ""
echo "After setup, the scraper will:"
echo "- Run automatically every 15 minutes"
echo "- Scrape Danish police RSS feeds"
echo "- Scrape DR and TV2 news"
echo "- Ingest incidents into your database"
echo ""
echo "Script complete!"
