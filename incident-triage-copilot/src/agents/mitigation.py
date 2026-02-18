"""Mitigation plan generator agent."""

from typing import List, Dict
from src.llm.ollama_client import OllamaClient
from src.models import IncidentContext
from src.storage.runbook_store import RunbookStore
from src.utils.logger import get_logger
import json

logger = get_logger(__name__)


class MitigationPlanner:
    """Generates mitigation plans with citations."""
    
    def __init__(
        self,
        llm_client: OllamaClient,
        runbook_store: RunbookStore
    ):
        self.llm = llm_client
        self.runbook_store = runbook_store
        logger.info("Initialized MitigationPlanner")
    
    def generate_plan(
        self,
        incident: IncidentContext,
        severity: str,
        category: str,
        root_causes: List[Dict],
        relevant_runbooks: List[Dict]
    ) -> Dict[str, any]:
        """Generate actionable mitigation plan with citations."""
        
        # Get full runbook content for top matches
        runbook_mitigation_steps = ""
        if relevant_runbooks:
            runbook_mitigation_steps = "\n\n--- MITIGATION STEPS FROM RUNBOOKS ---\n"
            for rb in relevant_runbooks[:2]:  # Top 2 runbooks
                content = self.runbook_store.get_runbook_by_path(rb["file_path"])
                if content and "## Immediate Mitigation" in content:
                    mitigation_section = content.split("## Immediate Mitigation")[1].split("##")[0]
                    runbook_mitigation_steps += f"\nFrom: {rb['title']}\n{mitigation_section}\n"
        
        system_prompt = """You are an expert SRE creating an incident mitigation plan. Your plan should be:
1. ACTIONABLE: Specific commands/steps, not vague suggestions
2. PRIORITIZED: Most critical steps first
3. CITED: Reference runbooks for each step
4. SAFE: Include rollback/validation steps

Respond with JSON only:
{
  "immediate_actions": [
    {
      "step": "<specific action>",
      "command": "<actual command if applicable>",
      "expected_outcome": "<what should happen>",
      "citation": "<runbook reference>"
    }
  ],
  "investigation_steps": [
    {
      "step": "<investigation action>",
      "citation": "<runbook reference>"
    }
  ],
  "escalation": {
    "when": "<conditions for escalation>",
    "who": "<team/person to escalate to>",
    "channel": "<communication channel>"
  },
  "summary": "<concise action plan summary>"
}"""

        alert = incident.alert
        root_cause_summary = "\n".join([
            f"- {rc['cause']} (likelihood: {rc['likelihood']:.0%})"
            for rc in root_causes
        ])
        
        prompt = f"""
Incident Context:
- Alert: {alert.alert_name}
- Severity: {severity}
- Category: {category}
- Affected Services: {', '.join(alert.affected_services)}

Root Causes Identified:
{root_cause_summary}

Metrics:
{json.dumps(alert.metrics, indent=2)}

{runbook_mitigation_steps}

Generate a detailed mitigation plan:"""

        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=2000
            )
            
            # Parse JSON response
            response_clean = response.strip()
            if response_clean.startswith("```"):
                lines = response_clean.split('\n')
                response_clean = '\n'.join([l for l in lines if not l.strip().startswith('```')])
            
            result = json.loads(response_clean)
            
            # Extract citations
            citations = []
            for action in result.get("immediate_actions", []):
                if action.get("citation"):
                    citations.append(action["citation"])
            for step in result.get("investigation_steps", []):
                if step.get("citation"):
                    citations.append(step["citation"])
            
            # Add runbook references
            citations.extend([rb["title"] for rb in relevant_runbooks])
            result["citations"] = list(set(citations))  # Remove duplicates
            
            logger.info(f"Generated mitigation plan with {len(result.get('immediate_actions', []))} immediate actions")
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse mitigation plan: {e}")
            logger.error(f"Response was: {response}")
            return {
                "immediate_actions": [
                    {
                        "step": "Review incident details manually",
                        "command": None,
                        "expected_outcome": "Better understanding of the issue",
                        "citation": "Default fallback"
                    }
                ],
                "investigation_steps": [],
                "escalation": {
                    "when": "If issue persists after 30 minutes",
                    "who": "On-call engineer",
                    "channel": "#incidents"
                },
                "summary": "Mitigation plan generation failed - manual intervention required",
                "citations": []
            }
        except Exception as e:
            logger.error(f"Error generating mitigation plan: {e}")
            raise
