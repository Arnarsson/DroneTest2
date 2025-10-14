# Chrome DevTools MCP Setup - Complete

**Date**: October 14, 2025
**Status**: ✅ Configuration Complete - Restart Required

---

## What Was Done

### 1. Verified Prerequisites ✅

**Chromium Installation**:
```bash
$ which chromium
/usr/bin/chromium

$ chromium --version
Chromium 141.0.7390.76 Arch Linux
```

**chrome-devtools-mcp Package**:
```bash
$ npx chrome-devtools-mcp@latest --version
0.8.1
```

**Test Run**:
```bash
$ npx chrome-devtools-mcp@latest --headless=true --isolated=true --executablePath=/usr/bin/chromium
chrome-devtools-mcp exposes content of the browser instance to the MCP clients...
✅ Server starts successfully
```

### 2. Created Global MCP Configuration ✅

**File**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--headless=true",
        "--isolated=true",
        "--executablePath=/usr/bin/chromium"
      ]
    }
  }
}
```

**Configuration Details**:
- `--headless=true`: Runs Chrome in headless mode (no GUI window)
- `--isolated=true`: Runs in isolated context for security
- `--executablePath=/usr/bin/chromium`: Uses system Chromium binary

### 3. Project-Level Configuration ✅

**File**: `.claude/.mcp.json` (already exists)

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--headless=true",
        "--isolated=true",
        "--executablePath=/usr/bin/chromium"
      ]
    }
  }
}
```

Both global and project-level configs are now in place.

---

## Next Steps (Required)

### 🔄 Step 1: Restart Claude Code

**MCP servers are loaded when Claude Code starts**, not during runtime.

**Options**:
1. **Close and reopen Claude Code** (full restart)
2. **Reload window** (if available in your environment)
3. Use **Command Palette** → "Reload Window" (if available)

### ✅ Step 2: Verify MCP Server is Loaded

After restarting, run:
```bash
/mcp
```

**Expected Output**:
```
MCP Servers:
  chrome-devtools (running)
    - Status: Connected
    - Tools: mcp__chrome-devtools__* (multiple tools available)
```

**If you see** "No MCP servers configured", the restart didn't take effect. Try:
1. Fully close and reopen Claude Code
2. Check Claude Code logs for MCP loading errors

### 🧪 Step 3: Test Chrome DevTools MCP

Once loaded, you'll have access to tools like:
- `mcp__chrome-devtools__navigate` - Navigate to URL
- `mcp__chrome-devtools__screenshot` - Take screenshot
- `mcp__chrome-devtools__console_logs` - Get console logs
- `mcp__chrome-devtools__execute_script` - Run JavaScript in browser

**Example Test**:
```
Claude, navigate to https://www.dronewatch.cc and check for console errors
```

Claude will use the MCP tools to:
1. Launch headless Chromium
2. Navigate to the URL
3. Capture console logs
4. Report any errors

---

## Troubleshooting

### Issue: /mcp shows "No MCP servers configured" after restart

**Possible Causes**:
1. Claude Code didn't fully restart
2. Config file has syntax error
3. MCP server failed to start

**Debug Steps**:

1. **Verify config file syntax**:
```bash
cat ~/.config/claude/claude_desktop_config.json | python3 -m json.tool
# Should print formatted JSON without errors
```

2. **Test MCP server manually**:
```bash
npx chrome-devtools-mcp@latest --headless=true --isolated=true --executablePath=/usr/bin/chromium
# Should print startup message without errors
```

3. **Check Claude Code logs**:
   - Look for MCP loading errors in Claude Code startup logs
   - Error messages will indicate what failed

4. **Verify Chromium can run headless**:
```bash
chromium --headless --disable-gpu --dump-dom https://example.com
# Should print HTML of example.com
```

### Issue: MCP server starts but Chrome crashes

**Possible Causes**:
- Chromium missing dependencies
- Sandboxing issues on Linux

**Fix**: Add `--no-sandbox` flag (less secure, use only if needed):
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--headless=true",
        "--isolated=true",
        "--executablePath=/usr/bin/chromium",
        "--no-sandbox"
      ]
    }
  }
}
```

### Issue: MCP tools not showing up

**Check**: Ensure you're calling tools with `mcp__` prefix
- ❌ Wrong: `chrome-devtools__navigate`
- ✅ Correct: `mcp__chrome-devtools__navigate`

---

## What This Enables

Once working, Chrome DevTools MCP allows:

### 1. Production Testing
```
Navigate to https://www.dronewatch.cc
Check for console errors
Verify API requests succeed
Take screenshot of the map
```

### 2. CORS Validation
```
Navigate to https://www.dronewatch.cc
Check network requests to https://www.dronemap.cc/api/incidents
Verify no CORS errors in console
```

### 3. Frontend Debugging
```
Navigate to production site
Execute JavaScript: document.querySelectorAll('.incident-marker').length
Get console logs for last 10 minutes
```

### 4. E2E Testing
```
Navigate to https://www.dronewatch.cc
Wait for map to load
Click on incident marker
Verify popup shows incident details
Take screenshot of result
```

### 5. Performance Monitoring
```
Navigate to production site
Measure page load time
Check for slow API requests
Capture performance metrics
```

---

## Alternative: Manual Browser Testing

If MCP setup continues to have issues, you can still verify production using:

### Option 1: Manual Browser with DevTools (F12)
1. Open https://www.dronewatch.cc in browser
2. Press F12 to open DevTools
3. Check Console tab for errors
4. Check Network tab for API requests
5. Verify no CORS errors

### Option 2: Curl Testing (Already Done)
```bash
# Test CORS headers
curl -X OPTIONS -I \
  -H "Origin: https://www.dronewatch.cc" \
  "https://www.dronemap.cc/api/incidents" | grep access-control

# Test API response
curl -s "https://www.dronemap.cc/api/incidents?limit=5" | python3 -m json.tool
```

**Result**: We already verified production is working correctly using curl in Wave 19 testing.

---

## Current Status

**What's Working Now**:
✅ Chromium installed and functional
✅ chrome-devtools-mcp package available (v0.8.1)
✅ MCP server can start successfully
✅ Global config created (`~/.config/claude/claude_desktop_config.json`)
✅ Project config exists (`.claude/.mcp.json`)
✅ Production verified working (via curl in Wave 19)

**What's Needed**:
🔄 **Restart Claude Code** to load MCP servers

**After Restart**:
- `/mcp` should show chrome-devtools server
- MCP tools will be available with `mcp__chrome-devtools__*` prefix
- Can perform browser-based testing of production site

---

## Documentation References

- **Chrome DevTools MCP**: https://github.com/modelcontextprotocol/servers/tree/main/src/chrome-devtools
- **Claude Code MCP Docs**: https://docs.claude.com/en/docs/claude-code/mcp
- **MCP Specification**: https://modelcontextprotocol.io/

---

**Setup Complete**: Ready for use after Claude Code restart ✅

**Last Updated**: October 14, 2025
**Tested On**: Arch Linux with Chromium 141.0.7390.76
