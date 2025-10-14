# Chrome DevTools MCP Troubleshooting Guide

**Issue**: MCP server cannot find Chromium executable despite correct configuration
**Status**: ⚠️ UNRESOLVED
**Date**: October 14, 2025

---

## Current Error

```
Could not find Google Chrome executable for channel 'stable' at:
 - /opt/google/chrome/chrome.
```

**Problem**: Server is looking for Chrome at wrong path (`/opt/google/chrome/chrome`) instead of configured Chromium path (`/usr/bin/chromium`)

---

## Configuration Status

**✅ CORRECT** - Both config files have proper syntax:

### `.claude/.mcp.json` (Project)
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--executable-path=/usr/bin/chromium",
        "--headless=true",
        "--isolated=true"
      ]
    }
  }
}
```

### `~/.config/claude/claude_desktop_config.json` (Global)
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--executable-path=/usr/bin/chromium",
        "--headless=true",
        "--isolated=true"
      ]
    }
  }
}
```

**Chromium Verified**:
```bash
$ which chromium
/usr/bin/chromium

$ chromium --version
Chromium 141.0.7390.76 Arch Linux
```

---

## Root Cause Analysis

The MCP server is **caching** the old configuration or **ignoring** the `--executable-path` argument.

**Possible Causes**:
1. **MCP Server Process Not Restarted**: The server started before config changes
2. **NPX Cache**: `chrome-devtools-mcp@latest` cached with old defaults
3. **Environment Variable Override**: System PATH or env vars overriding config
4. **chrome-devtools-mcp Bug**: Package may not respect `--executable-path` flag
5. **Permission Issue**: MCP server user can't access `/usr/bin/chromium`

---

## Troubleshooting Steps

### Step 1: Verify Chromium Accessibility

```bash
# Test as current user
/usr/bin/chromium --version
# Expected: Chromium 141.0.7390.76 Arch Linux

# Test headless mode
/usr/bin/chromium --headless --dump-dom https://example.com
# Expected: HTML output
```

### Step 2: Clear NPX Cache

```bash
# Clear NPX cache completely
npm cache clean --force

# Remove cached chrome-devtools-mcp
rm -rf ~/.npm/_npx/

# Test fresh install
npx chrome-devtools-mcp@latest --help
```

### Step 3: Manual Server Test

```bash
# Start MCP server manually with debug output
npx chrome-devtools-mcp@latest \
  --executable-path=/usr/bin/chromium \
  --headless=true \
  --isolated=true

# Check if it finds Chromium
# Expected: Server starts without "Could not find" error
```

### Step 4: Check chrome-devtools-mcp Version

```bash
# Check installed version
npm view chrome-devtools-mcp version

# Check what version is cached
npx chrome-devtools-mcp@latest --version

# Try specific version if latest is buggy
npx chrome-devtools-mcp@0.8.0 --help
```

### Step 5: Check Environment Variables

```bash
# Check if any Chrome-related env vars are set
env | grep -i chrome

# Check PATH
echo $PATH | tr ':' '\n' | grep -i chrome

# Check if CHROME_PATH or CHROMIUM_PATH is set
echo $CHROME_PATH
echo $CHROMIUM_PATH
```

### Step 6: Test with Alternative Browsers

```bash
# Try with Google Chrome (if installed)
sudo apt install google-chrome-stable  # Debian/Ubuntu
yay -S google-chrome  # Arch

# Update config to use Chrome
"--executable-path=/usr/bin/google-chrome"

# Or try Chromium from different location
"--executable-path=/usr/bin/chromium-browser"
```

### Step 7: Check MCP Server Logs

```bash
# Find MCP server process
ps aux | grep chrome-devtools-mcp

# Check Claude Code logs
~/.config/claude/logs/  # Check for MCP-related errors

# Run with verbose logging
npx chrome-devtools-mcp@latest \
  --executable-path=/usr/bin/chromium \
  --headless=true \
  --isolated=true \
  --verbose
```

### Step 8: Reinstall MCP Package

```bash
# Force reinstall
npm uninstall -g chrome-devtools-mcp
npm cache clean --force
npm install -g chrome-devtools-mcp@latest

# Or use specific version
npm install -g chrome-devtools-mcp@0.8.1
```

---

## Known Workarounds

### Workaround 1: Use Google Chrome Instead of Chromium

Install Google Chrome stable:
```bash
# Arch Linux
yay -S google-chrome

# Update config
"--executable-path=/usr/bin/google-chrome-stable"
```

### Workaround 2: Create Symlink

```bash
# Create symlink at expected location
sudo mkdir -p /opt/google/chrome
sudo ln -s /usr/bin/chromium /opt/google/chrome/chrome

# Restart Claude Code
```

### Workaround 3: Use Manual Browser Testing

Instead of Chrome DevTools MCP, use:
```bash
# Open browser manually
chromium --remote-debugging-port=9222 https://www.dronemap.cc

# Or use curl for API testing
curl -s https://www.dronemap.cc/api/incidents | jq

# Or use Playwright for E2E testing
npm install @playwright/test
npx playwright test
```

### Workaround 4: File a Bug Report

If none of the above work, this may be a bug in `chrome-devtools-mcp`:
```bash
# Check GitHub issues
https://github.com/modelcontextprotocol/servers/issues

# File new issue with details
- OS: Arch Linux
- Chromium version: 141.0.7390.76
- chrome-devtools-mcp version: latest
- Config: [paste your config]
- Error: "Could not find Google Chrome executable"
```

---

## Alternative Testing Methods

Since Chrome DevTools MCP is not working, use these alternatives:

### Method 1: Manual Browser Testing
```bash
# Open production site
chromium https://www.dronemap.cc

# Open DevTools (F12)
# - Check Console tab for errors
# - Check Network tab for API calls
# - Check Performance tab for metrics
```

### Method 2: API Testing with curl
```bash
# Test incidents endpoint
curl -s https://www.dronemap.cc/api/incidents | jq

# Test with filters
curl -s 'https://www.dronemap.cc/api/incidents?min_evidence=3' | jq 'length'

# Test CORS
curl -X OPTIONS -I -H "Origin: https://www.dronewatch.cc" \
  https://www.dronemap.cc/api/incidents
```

### Method 3: Playwright E2E Testing
```javascript
// test-production.js
const { chromium } = require('playwright');

async function test() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('https://www.dronemap.cc');
  await page.waitForLoadState('networkidle');

  // Check for errors
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  // Check API call
  const response = await page.waitForResponse(/api\/incidents/);
  const data = await response.json();

  console.log(`✅ ${data.length} incidents loaded`);
  console.log(`❌ ${errors.length} console errors`);

  await browser.close();
}

test();
```

---

## Success Criteria

**MCP Working When**:
- `mcp__chrome-devtools__new_page` creates page without error
- `mcp__chrome-devtools__list_pages` returns active pages
- `mcp__chrome-devtools__take_screenshot` captures images
- No "Could not find Google Chrome executable" errors

---

## Status Summary

**Configuration**: ✅ CORRECT
**Chromium**: ✅ INSTALLED AND WORKING
**MCP Server**: ❌ NOT FINDING CHROMIUM
**Workarounds**: ✅ AVAILABLE (manual browser, curl, Playwright)

**Recommendation**: Use manual browser testing (F12) or curl for now. File bug report with chrome-devtools-mcp maintainers if issue persists after trying all troubleshooting steps.

---

**Last Updated**: October 14, 2025 17:30 UTC
**Issue Tracker**: https://github.com/modelcontextprotocol/servers/issues
