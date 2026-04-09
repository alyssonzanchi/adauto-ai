# Rate Limiting Documentation

## Overview

The Car Ads Platform implements a robust rate limiting system using Redis and a sliding window algorithm. This protects the API from abuse while ensuring fair usage among all clients.

## Architecture

### Components

1. **RateLimiter** (`app.core.rate_limit.RateLimiter`)
   - Core rate limiting logic using Redis sorted sets
   - Implements sliding window algorithm
   - Tracks requests per time window

2. **RateLimitMiddleware** (`app.core.rate_limit.RateLimitMiddleware`)
   - FastAPI middleware for global rate limiting
   - Applied to all routes except `/health`, `/docs`, `/redoc`, `/openapi.json`
   - Adds rate limit headers to responses

3. **check_rate_limit** (`app.core.rate_limit.check_rate_limit`)
   - Dependency for per-endpoint custom rate limiting
   - Allows different limits for different endpoints

## Configuration

Rate limiting is configured via environment variables in `backend/.env`:

```bash
# Rate limiting configuration
RATE_LIMIT_PER_MINUTE=100    # Requests per minute (default: 100)
RATE_LIMIT_BURST=200         # Requests per hour/burst (default: 200)
```

## How It Works

### Sliding Window Algorithm

1. Each request is stored in Redis as a sorted set entry with timestamp as score
2. Old entries outside the time window are automatically removed
3. Current requests in the window are counted
4. Request is allowed if count < limit, otherwise denied with HTTP 429

### Identifier Priority

Rate limits are applied using this priority:

1. **User ID** - Extracted from JWT token (most accurate)
2. **API Key** - If implemented (future)
3. **IP Address** - Fallback for unauthenticated requests

For proxied requests, the real IP is extracted from `X-Forwarded-For` header.

## Usage

### Global Middleware (Automatic)

The middleware is automatically enabled and applies to all routes:

```python
# backend/app/main.py
from app.core.rate_limit import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    redis_client=redis,
    requests_per_minute=100,  # or use settings.RATE_LIMIT_PER_MINUTE
    requests_per_hour=200,    # or use settings.RATE_LIMIT_BURST
)
```

### Per-Endpoint Custom Limits

Use the `check_rate_limit` dependency for custom limits:

```python
from fastapi import APIRouter, Depends
from app.core.rate_limit import check_rate_limit

router = APIRouter()

# Strict limit for expensive operations
@router.get("/expensive")
async def expensive_endpoint(
    _: None = Depends(check_rate_limit(requests_per_minute=10))
):
    return {"data": "expensive computation result"}

# Both per-minute and per-hour limits
@router.post("/generate-report")
async def generate_report(
    _: None = Depends(check_rate_limit(
        requests_per_minute=5,
        requests_per_hour=50
    ))
):
    return {"report_id": "123"}

# Use default limits
@router.get("/search")
async def search(
    _: None = Depends(check_rate_limit())
):
    return {"results": []}
```

## Response Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1713456789
```

When limit is exceeded (HTTP 429):

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1713456789
Retry-After: 45
```

## Examples

See `backend/app/core/rate_limit_examples.py` for complete usage examples:

- Basic rate limiting
- Multiple limits (minute + hour)
- Strict limits for sensitive operations
- API endpoint rate limiting
- Admin endpoint rate limiting
- File upload rate limiting

## Testing

Run rate limiting tests:

```bash
cd backend
pytest tests/test_rate_limit.py -v
```

For integration tests (requires Redis):

```bash
pytest tests/test_rate_limit.py -v -m integration
```

## Best Practices

### 1. Choose Appropriate Limits

- **Public API**: 60-100 requests/minute
- **Authenticated**: 100-200 requests/minute
- **Expensive operations**: 5-20 requests/minute
- **Sensitive operations**: 3-10 requests/minute

### 2. Use Multiple Limits

For critical endpoints, use both per-minute and per-hour limits:

```python
@check_rate_limit(
    requests_per_minute=10,  # Prevent rapid bursts
    requests_per_hour=100    # Prevent abuse over time
)
```

### 3. Provide Clear Error Messages

When clients exceed limits, the error response includes:
- Clear error message
- Retry-After header
- Rate limit info in headers

### 4. Monitor and Adjust

- Monitor rate limit violations in logs
- Adjust limits based on usage patterns
- Consider business hours vs. off-hours
- Different tiers for different user plans

## Error Handling

### Redis Unavailable

If Redis is unavailable, the system **fails open**:
- Requests are allowed (not rate limited)
- Warning is logged
- Graceful degradation

### Invalid Tokens

If JWT token is invalid:
- Falls back to IP-based rate limiting
- No error is raised
- Rate limiting continues with IP

## Performance Considerations

### Redis Operations

Each rate limit check requires:
- 1 `ZREMRANGEBYSCORE` (remove old entries)
- 1 `ZCARD` (count current requests)
- 1 `ZADD` (add current request)
- 1 `EXPIRE` (set TTL)

Total: ~4 Redis operations per request

### Memory Usage

Each request in window uses:
- ~100 bytes in Redis (sorted set entry)
- Automatic cleanup via TTL

For 1000 users with 100 requests each:
- ~100KB in Redis
- Automatic expiration

### Scalability

- Redis can handle 100k+ operations/second
- Rate limiting adds ~1-2ms latency
- Suitable for high-traffic APIs

## Troubleshooting

### Rate Limiting Not Working

1. Check Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check connection:
   ```bash
   redis-cli info
   ```

3. Check logs for errors:
   ```bash
   tail -f backend/logs/app.log | grep rate
   ```

### All Requests Blocked

1. Check limits in `.env`:
   ```bash
   RATE_LIMIT_PER_MINUTE=100
   RATE_LIMIT_BURST=200
   ```

2. Check Redis for stuck keys:
   ```bash
   redis-cli
   > KEYS ratelimit:*
   > TTL ratelimit:user:123:minute
   ```

3. Clear stuck keys if needed:
   ```bash
   redis-cli
   > DEL ratelimit:user:123:minute
   ```

## Security Considerations

### IP Spoofing

- Rate limiting by IP is vulnerable to IP spoofing
- Always prefer user-based limits when authenticated
- Use X-Forwarded-For carefully (can be spoofed)

### DDoS Protection

- Rate limiting alone is not sufficient for DDoS
- Combine with:
  - Cloudflare/AWS Shield
  - Nginx rate limiting
  - Network-level protection

### Resource Exhaustion

- Monitor Redis memory usage
- Set appropriate TTLs
- Implement cleanup jobs
- Monitor for unusual patterns

## Future Enhancements

1. **API Key Rate Limiting**
   - Per-API key limits
   - Different tiers for different plans

2. **Rate Limiting by Endpoint**
   - Different limits for different endpoints
   - Cost-based limits (expensive ops)

3. **Dynamic Limits**
   - Adjust based on system load
   - Time-based limits (business hours)
   - Geographic limits

4. **Rate Limiting Analytics**
   - Track violations per user
   - Identify abuse patterns
   - Automatic blocking

5. **Distributed Rate Limiting**
   - Support for multiple Redis instances
   - Redis Cluster support
   - Cross-region rate limiting

## References

- [FastAPI Rate Limiting Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Redis Sorted Sets](https://redis.io/docs/data-types/sorted-sets/)
- [Rate Limiting Algorithms](https://konghq.com/blog/how-to-design-a-scalable-rate-limiting-algorithm/)
