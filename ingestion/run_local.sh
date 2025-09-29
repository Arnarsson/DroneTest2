#!/bin/bash

# DroneWatch Local Ingestion Runner
# Quick script to run ingestion locally

set -e

echo "🚁 DroneWatch Ingestion Runner"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
else
    echo "⚠️  No .env file found. Using defaults."
fi

# Parse command line arguments
TEST_MODE=""
if [ "$1" == "--test" ]; then
    TEST_MODE="--test"
    echo "🧪 Running in TEST MODE"
fi

# Run ingestion
echo "Starting ingestion..."
python ingest.py $TEST_MODE

echo "✅ Ingestion complete!"