# Kafka Consumer Lag

## Overview
Runbook for addressing Kafka consumer lag issues in message processing pipelines.

## Symptoms
- Consumer lag increasing beyond normal threshold (>1000 messages)
- Messages not being processed in timely manner
- Downstream services showing stale data
- Alert: "Kafka Consumer Lag Increasing"

## Root Causes
1. **Slow Consumer Processing**: Consumer taking too long per message
2. **Producer Spike**: Message production rate exceeds consumption rate
3. **Consumer Crashes**: Consumer pods restarting frequently
4. **Resource Constraints**: Consumer CPU/memory throttled
5. **Network Issues**: Slow network between Kafka and consumers
6. **Partition Imbalance**: Uneven distribution of messages across partitions

## Immediate Mitigation

### Step 1: Check Consumer Group Status
```bash
# View consumer group lag
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group order-processor-group --describe

# Check partition assignment
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group order-processor-group --members --describe
```

### Step 2: Scale Consumer Instances
```bash
# Increase consumer replicas
kubectl scale deployment order-processor --replicas=10

# Or use HPA
kubectl autoscale deployment order-processor \
  --cpu-percent=70 --min=3 --max=15
```

### Step 3: Check Consumer Health
```bash
# Check consumer pod status
kubectl get pods -l app=order-processor

# View consumer logs for errors
kubectl logs -l app=order-processor --tail=200 | grep ERROR

# Check resource usage
kubectl top pods -l app=order-processor
```

### Step 4: Optimize Consumer Performance
```yaml
# Increase consumer throughput
kafka:
  consumer:
    max-poll-records: 500  # Increase batch size
    fetch-min-bytes: 1048576  # 1MB
    concurrency: 10  # Parallel processing threads
```

### Step 5: Pause Non-Critical Consumers
If lag is critical, temporarily pause lower-priority consumer groups:
```bash
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group analytics-consumer-group --execute --reset-offsets \
  --to-current --all-topics
```

## Investigation Steps

### Analyze Message Processing Time
```bash
# Check consumer metrics
curl http://order-processor:8080/metrics | grep kafka_consumer

# Look for slow processing
# - Average processing time per message
# - 95th percentile processing time
```

### Check Kafka Broker Health
```bash
# Verify broker availability
kafka-broker-api-versions.sh --bootstrap-server kafka:9092

# Check topic partition count
kafka-topics.sh --bootstrap-server kafka:9092 \
  --topic order-processing --describe
```

### Review Recent Changes
- Recent deployments to consumer service
- Changes to message schema
- Database performance (if consumer writes to DB)

## Long-Term Solutions
1. **Partition Scaling**: Increase topic partitions for parallelism
2. **Consumer Optimization**: Profile and optimize message processing code
3. **Batching**: Process messages in larger batches
4. **Dead Letter Queue**: Move failed messages to DLQ instead of blocking
5. **Monitoring**: Set up lag monitoring and auto-scaling

## Related Runbooks
- [Kafka Broker Issues](kafka_broker.md)
- [Message Processing Optimization](message_optimization.md)

## Escalation
Escalate if lag continues growing after 30 minutes:
- **Team**: Data Platform
- **Slack**: #data-pipeline-incidents
- **PagerDuty**: Kafka on-call
