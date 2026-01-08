# Production Monitoring Guide

## Sentry Dashboard Access

**URL**: https://sentry.io/organizations/svc-cc/projects/dronewatch/

**Organization**: svc-cc  
**Project**: dronewatch

### Key Dashboards

1. **Issues Tab**: View all errors and exceptions
   - Filter by environment (production/development)
   - Group by error type or release
   - View error frequency and trends

2. **Performance Tab**: Monitor API response times
   - Transaction traces for API calls
   - Response time percentiles (p50, p75, p95, p99)
   - Slowest operations
   - Database query performance

3. **Releases Tab → Health**: Track release health
   - Crash-free session rate graphs
   - User adoption per release
   - Error distribution by release
   - Release comparison

4. **Dashboards Tab**: Custom metrics and visualizations
   - Real-time monitoring
   - Performance trends
   - Custom widgets

## Current Configuration

### Sample Rates (Production)
- **Traces**: 10% (`tracesSampleRate: 0.1`)
- **Sessions**: 100% (default)
- **Debug Mode**: Disabled in production

### Sample Rates (Development)
- **Traces**: 100% (`tracesSampleRate: 1.0`)
- **Debug Mode**: Enabled

## Setting Up Alerts

### 1. Error Rate Alerts

**Recommended**: Alert when error rate exceeds threshold

1. Go to **Alerts** → **Create Alert**
2. Set condition:
   - **Metric**: Error rate
   - **Threshold**: > 5 errors per minute
   - **Time Window**: 5 minutes
3. Set notification channels (email, Slack, etc.)

### 2. Performance Alerts

**Recommended**: Alert on slow API responses

1. Go to **Alerts** → **Create Alert**
2. Set condition:
   - **Metric**: Transaction duration (p95)
   - **Threshold**: > 2000ms
   - **Transaction**: `GET /api/incidents`
   - **Time Window**: 10 minutes

### 3. Crash-Free Rate Alerts

**Recommended**: Alert if crash-free rate drops

1. Go to **Alerts** → **Create Alert**
2. Set condition:
   - **Metric**: Crash-free session rate
   - **Threshold**: < 99%
   - **Time Window**: 1 hour

### 4. Release Health Alerts

**Recommended**: Alert on new release issues

1. Go to **Releases** → Select release → **Alerts**
2. Enable: "New issues in this release"
3. Set notification threshold (e.g., > 3 new issues)

## Monitoring Best Practices

### Daily Checks
- Review **Issues** tab for new errors
- Check **Performance** tab for slow transactions
- Review **Releases** tab for release health

### Weekly Reviews
- Analyze error trends
- Review performance metrics
- Check for regressions in new releases

### Monthly Analysis
- Review error resolution rate
- Analyze performance improvements
- Review user adoption metrics

## Key Metrics to Monitor

### Error Metrics
- **Error Rate**: Errors per minute
- **Error Types**: Most common errors
- **Affected Users**: Users experiencing errors
- **Resolution Time**: Time to fix errors

### Performance Metrics
- **API Response Time**: p50, p75, p95, p99
- **Database Query Time**: Slow queries
- **Page Load Time**: Frontend performance
- **Transaction Throughput**: Requests per second

### User Metrics
- **Crash-Free Rate**: % of sessions without crashes
- **User Adoption**: Active users per release
- **Session Duration**: Average session length

## Troubleshooting

### High Error Rate
1. Check **Issues** tab for error patterns
2. Review recent deployments
3. Check database connection issues
4. Review API rate limiting

### Slow Performance
1. Check **Performance** tab for slow transactions
2. Review database query performance
3. Check API response times
4. Review frontend bundle size

### Missing Data
1. Verify Sentry DSN is correct
2. Check sample rates (should be 10% in production)
3. Verify release tracking is working
4. Check browser console for errors

## Integration with CI/CD

### Release Tracking
Releases are automatically tracked via:
- `SENTRY_RELEASE` environment variable
- `NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA` (Vercel)
- Fallback: `dronewatch@{package.version}`

### Deployment Notifications
Configure Sentry to notify on:
- New errors in production
- Performance degradation
- Release health issues

## Rate Limiting Monitoring

API rate limiting is implemented with:
- **Limit**: 100 requests per minute per IP (configurable)
- **Window**: 60 seconds (configurable)
- **Response**: 429 status with `Retry-After` header
- **Backend**: Distributed via Upstash Redis (serverless-compatible)

Monitor rate limiting via:
- Sentry: Look for 429 errors
- Vercel logs: Check rate limit violations
- API response headers: `X-RateLimit-Remaining`
- Upstash dashboard: Monitor Redis usage

For detailed configuration and setup, see [API Rate Limiting](API_RATE_LIMITING.md).

## Security Monitoring

Monitor for:
- Authentication failures (401/403 errors)
- Rate limit violations (429 errors)
- Database connection errors
- Invalid environment variable errors

## Support

For Sentry issues:
- Documentation: https://docs.sentry.io/
- Support: https://sentry.io/support/

For DroneWatch monitoring:
- Check Vercel deployment logs
- Review GitHub Actions workflows
- Check database connection health (`/api/healthz`)

