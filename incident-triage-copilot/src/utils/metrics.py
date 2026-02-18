"""Metrics tracking for evaluation and monitoring."""

from datetime import datetime
from typing import Dict, List
import json


class MetricsTracker:
    """Track performance metrics for the triage copilot."""
    
    def __init__(self, feedback_file: str = "data/feedback.jsonl"):
        self.feedback_file = feedback_file
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "triages": []
        }
    
    def record_triage(
        self,
        incident_id: str,
        severity_predicted: str,
        category_predicted: str,
        root_causes: List[str],
        mitigation_plan: str,
        citations: List[str],
        processing_time: float
    ):
        """Record a triage result."""
        self.current_session["triages"].append({
            "incident_id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "severity_predicted": severity_predicted,
            "category_predicted": category_predicted,
            "root_causes": root_causes,
            "mitigation_plan": mitigation_plan,
            "citations": citations,
            "processing_time": processing_time
        })
    
    def record_feedback(
        self,
        incident_id: str,
        severity_actual: str,
        category_actual: str,
        root_cause_accuracy: float,
        mitigation_helpful: bool,
        notes: str = ""
    ):
        """Record feedback for a triage."""
        feedback = {
            "incident_id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "severity_actual": severity_actual,
            "category_actual": category_actual,
            "root_cause_accuracy": root_cause_accuracy,
            "mitigation_helpful": mitigation_helpful,
            "notes": notes
        }
        
        # Append to JSONL file
        with open(self.feedback_file, "a") as f:
            f.write(json.dumps(feedback) + "\n")
    
    def get_summary(self) -> Dict:
        """Get summary of current session metrics."""
        if not self.current_session["triages"]:
            return {"message": "No triages recorded yet"}
        
        avg_processing_time = sum(
            t["processing_time"] for t in self.current_session["triages"]
        ) / len(self.current_session["triages"])
        
        return {
            "total_triages": len(self.current_session["triages"]),
            "avg_processing_time": f"{avg_processing_time:.2f}s",
            "session_start": self.current_session["start_time"]
        }
