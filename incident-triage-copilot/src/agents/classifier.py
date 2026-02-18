"""Incident classifier agent."""

from typing import List, Dict
from src.llm.ollama_client import OllamaClient
from src.models import IncidentContext
from src.utils.logger import get_logger
import json

logger = get_logger(__name__)


class IncidentClassifier:
    """Classifies incidents by severity and category."""
    
    SEVERITY_LEVELS = ["SEV1", "SEV2", "SEV3", "SEV4"]
    CATEGORIES = [
        "Database",
        "API/Service",
        "Infrastructure",
        "Network",
        "Security",
        "Performance",
        "Data Pipeline",
        "Frontend"
    ]
    
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
        logger.info("Initialized IncidentClassifier")
    
    def classify(self, incident: IncidentContext) -> Dict[str, any]:
        """Classify incident severity and category."""
        
        system_prompt = """You are an expert SRE incident classifier. Focus on BUSINESS IMPACT, not just metrics.

Severity Classification (check ALL signals, not just one metric):

SEV1 (Critical) - Customer-impacting outage:
INDICATORS:
- Auth/payment/checkout services DOWN or degraded
- Error rate >5% on customer-facing endpoints
- Any "Connection refused", "Service unavailable", "Redis/DB down" in logs
- Failed transactions/requests >100/min
- Words: "unavailable", "down", "refused", "critical"
BUSINESS IMPACT: Revenue loss, customer complaints, SLA breach
EXAMPLE: "Auth service Redis down, 8.5% error rate, 1310 failed req/min" = SEV1

SEV2 (High) - Major degradation:
INDICATORS:
- Connection pool >85% utilized OR connection errors present
- Resource exhaustion approaching (>85% CPU/memory)
- Consumer lag >30,000 messages
- Error rate 2-5% or response time >3x normal
- Affects multiple services
- Words: "exhausted", "timeout", "lag increasing"
BUSINESS IMPACT: Partial functionality loss, some users affected
EXAMPLE: "DB pool 95/100, connection timeouts" = SEV2

SEV3 (Medium) - Performance degradation:
INDICATORS:
- Resource usage 70-85%
- Slow response times but no errors
- Consumer lag 10,000-30,000 messages
- Error rate <2%
- Limited user impact
BUSINESS IMPACT: Noticeable but manageable
EXAMPLE: "API latency 2x normal, no errors" = SEV3

SEV4 (Low) - Minor/internal:
- Internal tools only
- No customer impact
- Cosmetic issues

CRITICAL RULES:
1. Auth/Payment/Checkout DOWN = always SEV1 (even if error rate <10%)
2. Database connection issues + errors = SEV2 minimum  
3. Any "refused", "unavailable", "down" in auth/payment context = SEV1
4. Multiple affected services = upgrade severity by 1 level
5. When in doubt between SEV1/SEV2, choose SEV1 if customer-facing

Categories:
- Database: PostgreSQL, MySQL, connection pools, queries
- API/Service: REST APIs, microservices, auth, gateway
- Data Pipeline: Kafka, queues, ETL, stream processing
- Infrastructure: CPU, memory, disk, network
- Performance: Latency, throughput (non-specific)

Respond with JSON only:
{
  "severity": "SEV1|SEV2|SEV3|SEV4",
  "category": "<category>",
  "confidence": 0.0-1.0,
  "reasoning": "<cite specific metrics and business impact>"
}"""

        # Build incident summary
        alert = incident.alert
        incident_summary = f"""
Incident Alert:
- Alert Name: {alert.alert_name}
- Description: {alert.description}
- Source: {alert.source}
- Affected Services: {', '.join(alert.affected_services)}
- Environment: {alert.environment}
- Tags: {', '.join(alert.tags)}

Metrics:
{json.dumps(alert.metrics, indent=2)}
"""
        
        if incident.logs:
            incident_summary += f"\n\nRecent Logs:\n{incident.logs[:1000]}"  # Limit log size
        
        if incident.additional_context:
            incident_summary += f"\n\nAdditional Context:\n{incident.additional_context}"
        
        prompt = f"{incident_summary}\n\nClassify this incident:"
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            # Parse JSON response
            # Clean up response if it contains markdown code blocks
            response_clean = response.strip()
            if response_clean.startswith("```"):
                lines = response_clean.split('\n')
                response_clean = '\n'.join(lines[1:-1])
            
            result = json.loads(response_clean)
            
            # Validate result
            if result.get("severity") not in self.SEVERITY_LEVELS:
                logger.warning(f"Invalid severity: {result.get('severity')}, defaulting to SEV3")
                result["severity"] = "SEV3"
            
            if result.get("category") not in self.CATEGORIES:
                logger.warning(f"Invalid category: {result.get('category')}, defaulting to General")
                result["category"] = "Infrastructure"
            
            logger.info(f"Classified as {result['severity']} - {result['category']} (confidence: {result.get('confidence', 0)})")
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse classification response: {e}")
            logger.error(f"Response was: {response}")
            # Return default classification
            return {
                "severity": "SEV3",
                "category": "Infrastructure",
                "confidence": 0.3,
                "reasoning": "Classification failed, using default values"
            }
        except Exception as e:
            logger.error(f"Error during classification: {e}")
            raise
