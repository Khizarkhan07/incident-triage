# API Gateway 5xx Errors

## Overview
Runbook for troubleshooting and resolving API Gateway 5xx server errors.

## Symptoms
- Spike in HTTP 500/502/503/504 status codes
- Increased error rate in monitoring dashboards
- Customer reports of service unavailability
- Upstream service failures

## Root Causes
1. **Upstream Service Failure**: Backend services returning errors
2. **Circuit Breaker Activation**: Too many failures triggering circuit breaker
3. **Deployment Issues**: Recent deployment introduced bugs
4. **Resource Exhaustion**: CPU/Memory limits reached
5. **Dependency Failures**: External APIs or databases down
6. **Configuration Errors**: Invalid routing or timeout settings

## Immediate Mitigation

### Step 1: Identify Error Pattern
```bash
# Check error distribution by status code
kubectl logs -l app=api-gateway --tail=1000 | grep "HTTP/1.1 5" | awk '{print $9}' | sort | uniq -c

# Identify failing endpoints
kubectl logs -l app=api-gateway --tail=1000 | grep "500\|502\|503\|504"
```

### Step 2: Check Upstream Services
```bash
# Verify health of backend services
kubectl get pods -l tier=backend
kubectl top pods -l tier=backend

# Check specific service logs
kubectl logs -l app=auth-service --tail=100
```

### Step 3: Restart Unhealthy Pods
```bash
# Restart specific deployment
kubectl rollout restart deployment/auth-service

# Or delete specific unhealthy pods
kubectl delete pod <pod-name>
```

### Step 4: Open Circuit Breaker (if needed)
```bash
# Reset circuit breaker via admin endpoint
curl -X POST http://api-gateway/admin/circuit-breaker/auth-service/reset
```

### Step 5: Rollback Recent Deployment
```bash
# If errors started after recent deployment
kubectl rollout undo deployment/api-gateway
kubectl rollout undo deployment/auth-service
```

## Investigation Steps

### Check Recent Changes
1. Review recent deployments in last hour
2. Check configuration changes
3. Verify infrastructure changes (autoscaling, resources)

### Analyze Error Logs
Look for common patterns:
- NullPointerException → Code bug
- Connection refused → Service unavailable
- Timeout → Performance issue
- Out of memory → Resource constraint

### Verify Dependencies
- Database connectivity
- Redis cache availability
- External API accessibility

## Long-Term Solutions
1. **Improve Error Handling**: Add proper exception handling
2. **Circuit Breaker Tuning**: Adjust thresholds
3. **Resource Limits**: Right-size CPU/memory
4. **Retry Logic**: Implement exponential backoff
5. **Health Checks**: Improve liveness/readiness probes

## Related Runbooks
- [Service Mesh Troubleshooting](service_mesh.md)
- [Kubernetes Pod Debugging](k8s_debugging.md)

## Escalation
Escalate if unresolved within 20 minutes:
- **Team**: Platform Engineering
- **Slack**: #api-incidents
- **PagerDuty**: API on-call
