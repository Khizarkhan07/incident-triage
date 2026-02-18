"""Root cause analysis agent."""

from typing import List, Dict
from src.llm.ollama_client import OllamaClient
from src.models import IncidentContext
from src.storage.runbook_store import RunbookStore
from src.utils.logger import get_logger
import json

logger = get_logger(__name__)


class RootCauseAnalyzer:
    """Analyzes incidents to identify likely root causes."""
    
    def __init__(
        self,
        llm_client: OllamaClient,
        runbook_store: RunbookStore
    ):
        self.llm = llm_client
        self.runbook_store = runbook_store
        logger.info("Initialized RootCauseAnalyzer")
    
    def analyze(
        self,
        incident: IncidentContext,
        severity: str,
        category: str
    ) -> Dict[str, any]:
        """Analyze incident to determine likely root causes."""
        
        # Search for relevant runbooks
        search_query = f"{incident.alert.alert_name} {incident.alert.description}"
        all_runbooks = self.runbook_store.search_runbooks(
            query=search_query,
            top_k=3,
            category=category
        )
        
        # Filter by similarity threshold (0.3 = 30% minimum)
        SIMILARITY_THRESHOLD = 0.3
        relevant_runbooks = [rb for rb in all_runbooks if rb['similarity'] >= SIMILARITY_THRESHOLD]
        
        # Build context from runbooks
        runbook_context = ""
        if relevant_runbooks:
            runbook_context = "\n\n--- RELEVANT RUNBOOKS ---\n"
            for i, rb in enumerate(relevant_runbooks, 1):
                runbook_context += f"\n{i}. {rb['title']} (Similarity: {rb['similarity']:.2f})\n"
                # Extract root causes section
                content = rb['content']
                if "## Root Causes" in content:
                    root_section = content.split("## Root Causes")[1].split("##")[0]
                    runbook_context += f"{root_section[:500]}...\n"
        else:
            runbook_context = "\n\n--- No matching runbooks found (similarity < 30%). Using general SRE knowledge. ---\n"
        
        system_prompt = """You are an expert SRE performing root cause analysis. Analyze the incident and identify the most likely root causes based on:
1. The alert metrics and description
2. Error patterns in logs
3. Known issues from runbooks

Be specific and evidence-based. Cite concrete indicators from the data.

Respond with JSON only:
{
  "root_causes": [
    {
      "cause": "<specific root cause>",
      "likelihood": 0.0-1.0,
      "evidence": "<what in the data suggests this>"
    }
  ],
  "primary_cause": "<most likely root cause>",
  "reasoning": "<overall analysis>"
}"""

        alert = incident.alert
        prompt = f"""
Incident Details:
- Alert: {alert.alert_name}
- Description: {alert.description}
- Severity: {severity}
- Category: {category}
- Affected Services: {', '.join(alert.affected_services)}

Metrics:
{json.dumps(alert.metrics, indent=2)}

Logs:
{incident.logs[:1500] if incident.logs else 'No logs available'}

{runbook_context}

Analyze and identify root causes:"""

        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=1500
            )
            
            # Parse JSON response
            response_clean = response.strip()
            if response_clean.startswith("```"):
                lines = response_clean.split('\n')
                response_clean = '\n'.join([l for l in lines if not l.strip().startswith('```')])
            
            result = json.loads(response_clean)
            
            # Add runbook references
            result["relevant_runbooks"] = [
                {
                    "title": rb["title"],
                    "file_path": rb["file_path"],
                    "similarity": rb["similarity"]
                }
                for rb in relevant_runbooks
            ]
            
            logger.info(f"Identified {len(result.get('root_causes', []))} potential root causes")
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse root cause analysis: {e}")
            logger.error(f"Response was: {response}")
            return {
                "root_causes": [
                    {
                        "cause": "Unable to determine - analysis failed",
                        "likelihood": 0.3,
                        "evidence": "LLM response parsing error"
                    }
                ],
                "primary_cause": "Unknown",
                "reasoning": "Root cause analysis failed",
                "relevant_runbooks": []
            }
        except Exception as e:
            logger.error(f"Error during root cause analysis: {e}")
            raise
