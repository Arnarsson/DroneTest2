# API Rate Limiting

DroneWatch uses a distributed rate limiting system to protect the API from abuse while ensuring consistent limits across serverless instances.

## Overview

The rate limiting system uses a **sliding window algorithm** to track requests per client IP address. In production, limits are shared across all Vercel serverless function instances using **Upstash Redis**.

### Key Features

- **Distributed**: Limits are shared across all serverless instances
- **Sliding Window**: More accurate than fixed window algorithms
- **Fail-Open**: If Redis is unavailable, requests are allowed (with logging)
- **Configurable**: Limits can be customized via environment variables

---

## Rate Limit Headers

Every API response includes rate limit information in the headers:

| Header | Description | Example |
|--------|-------------|---------|
| `X-RateLimit-Limit` | Maximum requests allowed per window | `100` |
| `X-RateLimit-Remaining` | Requests remaining in current window | `75` |
| `X-RateLimit-Reset` | Unix timestamp when window resets | `1704672000` |
| `Retry-After` | Seconds until rate limit resets | `45` |

### Example Response Headers

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1704672000
Retry-After: 60
Content-Type: application/json
```

---

## Default Limits

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `RATE_LIMIT_MAX_REQUESTS` | `100` | Maximum requests per window |
| `RATE_LIMIT_WINDOW` | `60` | Window duration in seconds |

This means by default, each client IP address can make **100 requests per 60 seconds**.

---

## Rate Limited Responses

When the rate limit is exceeded, the API returns:

- **HTTP Status**: `429 Too Many Requests`
- **Response Body**: Error message explaining the limit
- **Headers**: Include `Retry-After` indicating when to retry

### Example 429 Response

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704672045
Retry-After: 45
Content-Type: application/json

{
  "detail": "Rate limit exceeded. Max 100 requests per 60 seconds."
}
```

---

## Configuring Custom Limits

Rate limits can be customized using environment variables:

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_MAX_REQUESTS` | `100` | Max requests per window |
| `RATE_LIMIT_WINDOW` | `60` | Window duration (seconds) |

### Example Configuration

In your Vercel Dashboard or `.env` file:

```bash
# Allow 200 requests per 2 minutes
RATE_LIMIT_MAX_REQUESTS=200
RATE_LIMIT_WINDOW=120
```

### Vercel Dashboard Configuration

1. Go to your project in the [Vercel Dashboard](https://vercel.com/dashboard)
2. Navigate to **Settings** > **Environment Variables**
3. Add the variables:
   - `RATE_LIMIT_MAX_REQUESTS`: Your desired limit
   - `RATE_LIMIT_WINDOW`: Window in seconds
4. Redeploy for changes to take effect

---

## Production Setup with Upstash Redis

For distributed rate limiting across Vercel serverless instances, you need to configure Upstash Redis.

### Why Upstash Redis?

In serverless environments, each function instance has its own memory. Without shared storage:
- Rate limits aren't shared across instances
- Attackers can bypass limits by hitting different instances
- Limits are reset on cold starts

Upstash Redis provides:
- **REST API**: No persistent connections (ideal for serverless)
- **Global replication**: Low latency worldwide
- **Free tier**: 10,000 requests/day

### Setup Instructions

#### 1. Create Upstash Account

1. Go to [upstash.com](https://upstash.com/)
2. Sign up for a free account
3. Create a new Redis database

#### 2. Get Credentials

From your Upstash dashboard:

1. Select your Redis database
2. Find the **REST API** section
3. Copy the **REST URL** and **REST Token**

#### 3. Configure Environment Variables

Add to your Vercel project:

```bash
# Upstash Redis Configuration
UPSTASH_REDIS_REST_URL=https://your-database.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-upstash-token
```

**In Vercel Dashboard:**
1. Go to **Settings** > **Environment Variables**
2. Add `UPSTASH_REDIS_REST_URL` with your REST URL
3. Add `UPSTASH_REDIS_REST_TOKEN` with your REST Token
4. Redeploy for changes to take effect

#### 4. Verify Setup

After deployment, you can verify Redis is working by:
- Checking Vercel function logs for "Upstash Redis client initialized successfully"
- Monitoring the Upstash dashboard for requests

---

## Local Development

For local development, Upstash Redis is **optional**. The rate limiter automatically falls back to in-memory storage when:

- `UPSTASH_REDIS_REST_URL` is not set
- `UPSTASH_REDIS_REST_TOKEN` is not set
- Redis connection fails

A warning will be logged:
```
Upstash Redis not configured. Falling back to in-memory rate limiting.
```

This fallback is perfect for local development but **not suitable for production** serverless deployments.

---

## Client IP Detection

The rate limiter extracts client IP addresses from the following headers (in order of priority):

1. `X-Forwarded-For` (first IP in the list)
2. `X-Real-IP`
3. `Remote-Addr`

Vercel automatically sets the `X-Forwarded-For` header with the original client IP.

---

## Best Practices for API Clients

### Handling Rate Limits

```javascript
async function fetchWithRateLimit(url) {
  const response = await fetch(url);

  // Check remaining requests
  const remaining = response.headers.get('X-RateLimit-Remaining');
  console.log(`Requests remaining: ${remaining}`);

  if (response.status === 429) {
    // Rate limited - wait and retry
    const retryAfter = response.headers.get('Retry-After');
    console.log(`Rate limited. Retry after ${retryAfter} seconds`);

    await new Promise(resolve =>
      setTimeout(resolve, parseInt(retryAfter) * 1000)
    );

    return fetchWithRateLimit(url);
  }

  return response;
}
```

### Implementing Exponential Backoff

```javascript
async function fetchWithBackoff(url, maxRetries = 3) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await fetch(url);

    if (response.status !== 429) {
      return response;
    }

    if (attempt === maxRetries) {
      throw new Error('Max retries exceeded');
    }

    // Exponential backoff: 1s, 2s, 4s...
    const delay = Math.pow(2, attempt) * 1000;
    await new Promise(resolve => setTimeout(resolve, delay));
  }
}
```

### Monitoring Your Usage

Check the `X-RateLimit-Remaining` header to monitor your usage and adjust request frequency before hitting limits.

---

## Monitoring Rate Limits

### Vercel Logs

Rate limit violations are logged with:
- Client IP address
- Request path
- Current count vs limit

### Sentry Integration

429 errors are captured in Sentry. Monitor for:
- High rate limit violation rates
- Potential abuse patterns
- Geographic distribution of violations

### Upstash Dashboard

Monitor Redis usage:
- Total requests per day
- Key count (active rate limit buckets)
- Memory usage

---

## Security Considerations

### IP Spoofing

The `X-Forwarded-For` header can be spoofed in some configurations. Vercel sets this header correctly and overwrites any client-provided value.

### Fail-Open Behavior

If Redis is unavailable, the rate limiter allows requests (fail-open). This prevents service outages but may allow abuse during Redis downtime. Monitor for:
- Redis availability
- Unusual traffic patterns during outages

### Distributed Denial of Service (DDoS)

Rate limiting provides protection against simple attacks. For sophisticated DDoS attacks, consider:
- Vercel's built-in DDoS protection
- Cloudflare or similar CDN protection
- Application-level anomaly detection

---

## Troubleshooting

### Rate Limits Not Working in Production

**Symptom**: Different serverless instances have different rate counts

**Solution**: Ensure Upstash Redis is configured:
```bash
# Verify environment variables are set
echo $UPSTASH_REDIS_REST_URL
echo $UPSTASH_REDIS_REST_TOKEN
```

### Fallback Warning in Logs

**Symptom**: "Falling back to in-memory rate limiting" warning

**Solutions**:
1. Verify Upstash credentials are correct
2. Check Upstash dashboard for service issues
3. Ensure `upstash-redis` package is installed

### 429 Errors for Legitimate Users

**Symptom**: Users hitting rate limits unexpectedly

**Solutions**:
1. Increase `RATE_LIMIT_MAX_REQUESTS`
2. Check for shared IP addresses (corporate networks, VPNs)
3. Review client implementation for unnecessary requests

---

## API Reference

### Functions

#### `check_rate_limit(ip: str) -> Tuple[bool, int, int]`

Check if an IP is within rate limits.

**Returns**: `(allowed, remaining, reset_after)`
- `allowed`: True if request is allowed
- `remaining`: Requests remaining in window
- `reset_after`: Seconds until window resets

#### `get_rate_limit_headers(remaining: int, reset_after: int) -> Dict[str, str]`

Get rate limit headers for response.

**Returns**: Dictionary with headers:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After`

#### `get_client_ip(headers: dict) -> str`

Extract client IP from request headers.

**Returns**: Client IP address string

#### `is_redis_available() -> bool`

Check if Redis is available for health checks.

**Returns**: True if Redis is connected and responding

---

## Related Documentation

- [Backend API](development/backend/README.md) - API endpoints and deployment
- [Monitoring Guide](MONITORING.md) - Error tracking and alerts
- [Environment Variables](development/backend/README.md#3-set-environment-variables) - Configuration reference

---

**Last Updated**: January 2026
**Module**: `frontend/api/distributed_rate_limit.py`
