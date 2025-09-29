#!/bin/bash

echo "=== DEBUG: Build Environment ==="
echo "Current directory: $(pwd)"
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"
echo "Python version: $(python3 --version)"

echo ""
echo "=== DEBUG: Directory Structure ==="
echo "Contents of root:"
ls -la

echo ""
echo "=== DEBUG: Checking for frontend directory ==="
if [ -d "frontend" ]; then
    echo "✅ frontend directory exists"
    echo "Contents of frontend:"
    ls -la frontend/

    echo ""
    echo "=== DEBUG: Checking frontend/package.json ==="
    if [ -f "frontend/package.json" ]; then
        echo "✅ frontend/package.json exists"
        cat frontend/package.json | head -20
    else
        echo "❌ frontend/package.json NOT FOUND"
    fi
else
    echo "❌ frontend directory NOT FOUND"
fi

echo ""
echo "=== DEBUG: Checking for API directory ==="
if [ -d "api" ]; then
    echo "✅ api directory exists"
    ls -la api/
else
    echo "❌ api directory NOT FOUND"
fi

echo ""
echo "=== DEBUG: Environment Variables ==="
echo "VERCEL: $VERCEL"
echo "VERCEL_ENV: $VERCEL_ENV"
echo "VERCEL_URL: $VERCEL_URL"
echo "VERCEL_REGION: $VERCEL_REGION"

echo ""
echo "=== DEBUG: Attempting to build ==="
if [ -d "frontend" ]; then
    echo "Entering frontend directory..."
    cd frontend
    echo "Current directory after cd: $(pwd)"
    echo "Installing dependencies..."
    npm install
    echo "Building Next.js app..."
    npm run build
else
    echo "ERROR: Cannot cd to frontend - directory not found!"
    exit 1
fi