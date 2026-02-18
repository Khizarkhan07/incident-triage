# Redis Memory Exhaustion

## Overview
Runbook for handling Redis cache memory exhaustion and high eviction rates.

## Symptoms
- Redis memory usage > 90%
- High eviction rate (cache keys being removed prematurely)
- Cache hit rate dropping significantly
- Application performance degradation
- Increased database load (cache misses)

## Root Causes
1. **Memory Leak**: Keys not expiring properly, TTL not set
2. **Data Growth**: Legitimate increase in cached data volume
3. **Large Values**: Storing oversized objects in cache
4. **No Eviction Policy**: Incorrect or missing eviction configuration
5. **Memory Limit Too Low**: Insufficient memory allocated to Redis

## Immediate Mitigation

### Step 1: Check Memory Status
```bash
# Connect to Redis
redis-cli -h redis-cluster -p 6379

# Check memory info
INFO memory

# Check eviction stats
INFO stats | grep evicted

# Find memory usage by key pattern
redis-cli --bigkeys
```

### Step 2: Clear Non-Critical Cache
```bash
# Identify and clear temporary/stale data
KEYS temp:*
SCAN 0 MATCH session:expired:* COUNT 1000

# Clear specific key patterns (BE CAREFUL)
redis-cli --scan --pattern "cache:old:*" | xargs redis-cli DEL
```

### Step 3: Increase Memory Limit (Temporary)
```bash
# For Redis in Kubernetes
kubectl set resources deployment redis \
  --limits=memory=8Gi --requests=memory=8Gi

# Or modify redis.conf
maxmemory 8gb
```

### Step 4: Optimize Eviction Policy
```bash
# Set appropriate eviction policy
CONFIG SET maxmemory-policy allkeys-lru

# Common policies:
# - allkeys-lru: Evict any key using LRU
# - volatile-lru: Evict keys with TTL using LRU
# - allkeys-lfu: Evict any key using LFU (Least Frequently Used)
```

### Step 5: Restart Redis (Last Resort)
```bash
# Only if memory is critically full and evictions failing
kubectl rollout restart deployment/redis

# Ensure persistence is configured to avoid data loss
```

## Investigation Steps

### Identify Memory Hogs
```bash
# Find largest keys
redis-cli --bigkeys

# Sample memory usage by key type
redis-cli --memkeys

# Check specific key size
DEBUG OBJECT <key-name>
MEMORY USAGE <key-name>
```

### Analyze Key Patterns
```bash
# Count keys by pattern
redis-cli KEYS "session:*" | wc -l
redis-cli KEYS "product:*" | wc -l
redis-cli KEYS "user:*" | wc -l

# Check TTL distribution
redis-cli --scan --pattern "*" | while read key; do 
  echo "$key $(redis-cli TTL $key)"; 
done | sort -k2 -n
```

### Review Application Usage
1. Check which services are writing to Redis
2. Verify TTL is set on cached objects
3. Review cache invalidation logic
4. Identify any infinite loops or cache stampede

## Long-Term Solutions

### 1. Implement Proper TTL Strategy
```python
# Always set TTL when caching
redis.setex("user:123", 3600, user_data)  # 1 hour TTL

# Use sliding expiration for hot data
redis.expire("product:456", 7200)
```

### 2. Cache Size Limits
```python
# Limit collection sizes
redis.lpush("recent_orders:user:123", order_id)
redis.ltrim("recent_orders:user:123", 0, 99)  # Keep only 100 items
```

### 3. Add Read Replicas
Scale reads across multiple Redis instances.

### 4. Partition Cache
Split cache across multiple Redis clusters by key pattern.

### 5. Monitor Cache Effectiveness
- Track cache hit/miss ratio
- Monitor eviction rate
- Alert on memory thresholds (>85%)

## Related Runbooks
- [Cache Strategy Best Practices](cache_strategy.md)
- [Redis Cluster Scaling](redis_scaling.md)

## Escalation
Escalate if memory remains critical after 15 minutes:
- **Team**: Infrastructure SRE
- **Slack**: #cache-incidents
- **PagerDuty**: Redis on-call
