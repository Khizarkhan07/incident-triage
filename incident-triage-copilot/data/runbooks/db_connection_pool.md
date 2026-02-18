# Database Connection Pool Exhaustion

## Overview
Runbook for handling PostgreSQL connection pool exhaustion incidents.

## Symptoms
- Increased database connection timeout errors
- Application timeouts when accessing database
- Active connections approaching or at max_connections limit
- HTTP 503 Service Unavailable errors from backend services

## Root Causes
1. **Connection Leak**: Application not properly closing connections
2. **Traffic Spike**: Sudden increase in concurrent users
3. **Long-Running Queries**: Queries holding connections for extended periods
4. **Insufficient Pool Size**: Pool max_connections set too low for load
5. **Database Resource Exhaustion**: Database server CPU/memory constraints

## Immediate Mitigation

### Step 1: Verify Current State
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Identify long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;
```

### Step 2: Terminate Long-Running Queries (if safe)
```sql
-- Terminate specific query
SELECT pg_terminate_backend(PID);

-- Terminate all idle connections older than 5 minutes
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND now() - state_change > interval '5 minutes';
```

### Step 3: Scale Application Pool
```yaml
# Temporarily increase pool size in application config
database:
  hikari:
    maximum-pool-size: 150  # Increase from 100
    connection-timeout: 45000
```

### Step 4: Add Read Replicas (if applicable)
Route read-only queries to read replicas to reduce load on primary.

## Long-Term Solutions
1. **Connection Pooling Audit**: Review application code for connection leaks
2. **Query Optimization**: Optimize slow queries identified in monitoring
3. **Database Scaling**: Increase database instance size if needed
4. **Connection Limits**: Set appropriate limits per service
5. **Monitoring**: Add alerts for connection pool metrics

## Related Runbooks
- [Query Performance Tuning](query_optimization.md)
- [Database Scaling](db_scaling.md)

## Escalation
If mitigation steps don't resolve within 15 minutes, escalate to:
- **Team**: Database SRE
- **Slack**: #database-incidents
- **PagerDuty**: Database on-call engineer
