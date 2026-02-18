"""Orchestrator for the incident triage copilot."""

import time
from typing import Dict
from src.llm.ollama_client import OllamaClient
from src.storage.runbook_store import RunbookStore
from src.agents.classifier import IncidentClassifier
from src.agents.root_cause import RootCauseAnalyzer
from src.agents.mitigation import MitigationPlanner
from src.models import IncidentContext, TriageResult
from src.utils.logger import get_logger
from src.utils.metrics import MetricsTracker

logger = get_logger(__name__)


class TriageOrchestrator:
    """Orchestrates the incident triage process."""
    
    def __init__(
        self,
        llm_client: OllamaClient,
        runbook_store: RunbookStore,
        metrics_tracker: MetricsTracker
    ):
        self.llm = llm_client
        self.runbook_store = runbook_store
        self.metrics = metrics_tracker
        
        # Initialize agents
        self.classifier = IncidentClassifier(llm_client)
        self.root_cause_analyzer = RootCauseAnalyzer(llm_client, runbook_store)
        self.mitigation_planner = MitigationPlanner(llm_client, runbook_store)
        
        logger.info("Initialized TriageOrchestrator")
    
    def triage_incident(self, incident: IncidentContext) -> TriageResult:
        """Perform end-to-end incident triage."""
        start_time = time.time()
        
        logger.info(f"Starting triage for incident: {incident.alert.incident_id}")
        
        # Step 1: Classify incident
        logger.info("Step 1: Classifying incident...")
        classification = self.classifier.classify(incident)
        
        # Step 2: Analyze root causes
        logger.info("Step 2: Analyzing root causes...")
        root_cause_analysis = self.root_cause_analyzer.analyze(
            incident=incident,
            severity=classification["severity"],
            category=classification["category"]
        )
        
        # Step 3: Generate mitigation plan
        logger.info("Step 3: Generating mitigation plan...")
        mitigation = self.mitigation_planner.generate_plan(
            incident=incident,
            severity=classification["severity"],
            category=classification["category"],
            root_causes=root_cause_analysis.get("root_causes", []),
            relevant_runbooks=root_cause_analysis.get("relevant_runbooks", [])
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Build triage result
        result = TriageResult(
            incident_id=incident.alert.incident_id,
            severity=classification["severity"],
            category=classification["category"],
            confidence_score=classification.get("confidence", 0.0),
            root_causes=[rc["cause"] for rc in root_cause_analysis.get("root_causes", [])],
            mitigation_plan=self._format_mitigation_plan(mitigation),
            relevant_runbooks=root_cause_analysis.get("relevant_runbooks", []),
            citations=mitigation.get("citations", []),
            reasoning=classification.get("reasoning", ""),
            processing_time=processing_time
        )
        
        # Record metrics
        self.metrics.record_triage(
            incident_id=incident.alert.incident_id,
            severity_predicted=result.severity,
            category_predicted=result.category,
            root_causes=result.root_causes,
            mitigation_plan=result.mitigation_plan,
            citations=result.citations,
            processing_time=processing_time
        )
        
        logger.info(f"Triage completed in {processing_time:.2f}s")
        return result
    
    def _format_mitigation_plan(self, mitigation: Dict) -> str:
        """Format mitigation plan for display."""
        plan = "## 🚨 Immediate Actions\n\n"
        
        for i, action in enumerate(mitigation.get("immediate_actions", []), 1):
            plan += f"**{i}. {action['step']}**\n"
            if action.get("command"):
                plan += f"```bash\n{action['command']}\n```\n"
            plan += f"✅ Expected: {action['expected_outcome']}\n"
            if action.get("citation"):
                plan += f"📖 Source: {action['citation']}\n"
            plan += "\n"
        
        if mitigation.get("investigation_steps"):
            plan += "\n## 🔍 Investigation Steps\n\n"
            for i, step in enumerate(mitigation.get("investigation_steps", []), 1):
                plan += f"{i}. {step['step']}\n"
                if step.get("citation"):
                    plan += f"   📖 {step['citation']}\n"
        
        if mitigation.get("escalation"):
            esc = mitigation["escalation"]
            plan += f"\n## 📞 Escalation\n\n"
            plan += f"**When:** {esc.get('when', 'As needed')}\n"
            plan += f"**Who:** {esc.get('who', 'On-call team')}\n"
            plan += f"**Channel:** {esc.get('channel', '#incidents')}\n"
        
        return plan
