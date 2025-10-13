# Sentry Setup Complete - DroneWatch
**Date**: October 13, 2025
**Status**: ✅ Configured & Deployed

---

## Setup Summary

### ✅ Completed Configuration

1. **Sentry SDK Installed**: @sentry/nextjs v10.19.0
2. **Wizard Executed**: Authenticated with svc-cc/dronewatch project
3. **Release Health Enabled**: Session tracking and crash-free statistics
4. **Browser Tracing**: Performance monitoring for API calls
5. **Console Integration**: Automatic log capture (log, warn, error)

### Configuration Files Created

```
frontend/
├── sentry.client.config.ts    # Browser-side config
├── sentry.server.config.ts    # Server-side config
├── sentry.edge.config.ts      # Edge runtime config
├── instrumentation.ts         # Runtime hooks
└── next.config.js             # withSentryConfig wrapper
```

### Release Tracking

**Release ID Strategy**:
```javascript
SENTRY_RELEASE env var
→ NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA (Vercel)
→ dronewatch@{package.version} (fallback)
```

**Current Release**: `dronewatch@0.1.0` or git commit SHA

### Health Metrics Enabled

- ✅ Session tracking (autoSessionTracking: true)
- ✅ Crash-free session rate (sessionSampleRate: 100%)
- ✅ Error tracking by release
- ✅ Performance tracing (tracesSampleRate: 100%)
- ✅ Console log capture (log, warn, error)

### Instrumented Code

**useIncidents Hook** (`frontend/hooks/useIncidents.ts`):
```typescript
// Sentry span wrapping
Sentry.startSpan({
  op: "http.client",
  name: "GET /api/incidents",
}, async (span) => {
  span.setAttribute("api_url", API_URL)
  span.setAttribute("filters", JSON.stringify(filters))
  span.setAttribute("http.status_code", response.status)
  span.setAttribute("incident_count", data.length)

  // Capture warnings
  if (data.length === 0) {
    Sentry.captureMessage('API returned empty array', {
      level: 'warning',
      extra: { url, filters }
    })
  }
})
```

---

## How to Access Sentry Dashboard

### 1. Login
- URL: https://sentry.io
- Organization: `svc-cc`
- Project: `dronewatch`

### 2. Key Dashboards

**Issues Tab**:
- View all errors and exceptions
- Group by error type or release
- Filter by environment (production/development)

**Performance Tab**:
- Transaction traces for API calls
- Response time percentiles
- Slowest operations

**Releases Tab → Health**:
- Crash-free session rate graphs
- User adoption per release
- Error distribution by release
- Release comparison

**Dashboards Tab**:
- Custom metrics and visualizations
- Real-time monitoring
- Performance trends

### 3. What to Look For

**For the "0 incidents" issue**:
1. Go to **Performance** → **Transactions**
2. Look for `GET /api/incidents` traces
3. Check:
   - Is the fetch being called?
   - What's the response time?
   - What status code is returned?
   - Are there any errors?

4. Go to **Issues**
5. Filter by `level:warning`
6. Look for "API returned empty array" messages

7. Go to **Logs** (if enabled)
8. Search for `[useIncidents]` console logs
9. Check the actual API URL being used

---

## Current Problem Status

### Issue: Frontend Shows 0 Incidents

**Symptoms**:
- Debug Panel: "API Data: 0 incidents"
- Debug Panel: "Loading: YES" (infinite)
- Debug Panel: "Error: NO"
- Map: Empty (no markers)

**Verified Working**:
- ✅ API endpoint: `https://www.dronemap.cc/api/incidents` returns 7 incidents
- ✅ CORS headers: `access-control-allow-origin: *`
- ✅ Response time: <500ms
- ✅ Status code: 200 OK
- ✅ Data format: Valid JSON array

**Not Working**:
- ❌ Frontend React Query not receiving data
- ❌ useIncidents hook stuck in loading state
- ❌ No errors thrown or captured

### Next Debugging Steps

1. **Check Sentry Performance Tab**:
   - Are there any `GET /api/incidents` traces?
   - If YES: Check span attributes (api_url, incident_count)
   - If NO: Frontend isn't even making the request

2. **Check Sentry Issues Tab**:
   - Look for "API returned empty array" warnings
   - Check if there are any uncaught exceptions
   - Filter by last 24 hours

3. **Check Sentry Logs**:
   - Search for `[useIncidents]` console output
   - See the exact API URL being constructed
   - Check if fetch is completing or timing out

4. **Potential Root Causes**:
   - React Query cache staleness
   - Environment variable not embedded at build time
   - Service Worker caching old responses
   - Browser cache showing old deployment
   - Build-time code splitting issue

---

## Sentry Integration Benefits

### Immediate Visibility
- **Real-time error capture**: See errors as they happen
- **Performance monitoring**: Track API response times
- **Console logs**: View production console output
- **User sessions**: Track crash-free rates

### Debugging Power
- **Full stack traces**: Know exactly where errors occur
- **Breadcrumbs**: See user actions leading to errors
- **Context**: Environment, release, user data
- **Search & filter**: Find specific issues quickly

### Release Management
- **Compare releases**: See impact of each deployment
- **Regression detection**: Identify new errors
- **Adoption tracking**: Monitor user uptake
- **Rollback decisions**: Data-driven deployment choices

---

## Production Deployments

### Latest Deployments
1. **Commit 3a601f9**: Sentry Release Health tracking
   - Session monitoring enabled
   - Release tagging configured
   - Browser tracing added

2. **Commit 8226c63**: Initial Sentry integration
   - Error capture
   - Console logging
   - HTTP client tracing

3. **Commit fd11cc5**: Debug test page
   - Environment variable logging
   - Direct API test

4. **Commit 5dda405**: API diagnostic test
   - Simple fetch test
   - CORS verification

### Build Status
- **Platform**: Vercel
- **Framework**: Next.js 14.2.18
- **Runtime**: Node.js 18
- **Deploy Trigger**: Push to `main` branch
- **Build Time**: ~2-3 minutes

---

## Configuration Reference

### Environment Variables (Vercel)

**Required**:
- `DATABASE_URL`: Supabase connection
- `INGEST_TOKEN`: Scraper authentication
- `NEXT_PUBLIC_API_URL`: Frontend API endpoint

**Sentry** (Optional):
- `SENTRY_AUTH_TOKEN`: For source map uploads
- `SENTRY_ORG`: svc-cc
- `SENTRY_PROJECT`: dronewatch

### Sample Rates (Current)

```typescript
tracesSampleRate: 1.0        // 100% - capture all traces
sessionSampleRate: 1.0       // 100% - track all sessions
debug: NODE_ENV === 'development'  // verbose logging in dev
```

**Production Recommendations**:
```typescript
tracesSampleRate: 0.1        // 10% - reduce noise
sessionSampleRate: 0.2       // 20% - representative sample
debug: false                 // disable in production
```

---

## Support & Resources

**Sentry Documentation**:
- Next.js Guide: https://docs.sentry.io/platforms/javascript/guides/nextjs/
- Release Health: https://docs.sentry.io/product/releases/health/
- Performance: https://docs.sentry.io/product/performance/

**Project Links**:
- Sentry Dashboard: https://sentry.io/organizations/svc-cc/projects/dronewatch/
- Production Site: https://www.dronemap.cc
- Repository: https://github.com/Arnarsson/DroneWatch2.0

**Created**: October 13, 2025
**Last Updated**: October 13, 2025
**Version**: 1.0
