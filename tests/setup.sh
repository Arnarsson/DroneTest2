#!/bin/bash

# DroneWatch 2.0 - E2E Test Setup Script
# This script sets up the Playwright testing environment

set -e  # Exit on error

echo "🚀 Setting up DroneWatch E2E Tests..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo ""

# Navigate to tests directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing npm dependencies..."
npm install

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
npx playwright install

# Install system dependencies (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Installing system dependencies for Linux..."
    npx playwright install-deps
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo ""
echo "  1. Run all tests:"
echo "     npm test"
echo ""
echo "  2. Run tests in headed mode (see browser):"
echo "     npm run test:headed"
echo ""
echo "  3. Run tests in UI mode (interactive):"
echo "     npm run test:ui"
echo ""
echo "  4. Run specific browser:"
echo "     npm run test:chromium"
echo "     npm run test:firefox"
echo "     npm run test:webkit"
echo ""
echo "  5. View test report after running:"
echo "     npm run report"
echo ""
echo "📖 For more info, see: tests/README.md"
echo ""
