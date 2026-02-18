"""Evaluation engine for the triage copilot."""

import json
from pathlib import Path
from typing import List, Dict
from src.models import IncidentContext, IncidentAlert, TriageResult
from src.orchestrator import TriageOrchestrator
from src.utils.logger import get_logger
from sklearn.metrics import accuracy_score, precision_score

logger = get_logger(__name__)


class TriageEvaluator:
    """Evaluates triage performance against golden cases."""
    
    def __init__(
        self,
        orchestrator: TriageOrchestrator,
        golden_cases_dir: str = "data/golden_cases"
    ):
        self.orchestrator = orchestrator
        self.golden_cases_dir = Path(golden_cases_dir)
        logger.info("Initialized TriageEvaluator")
    
    def load_golden_cases(self) -> List[Dict]:
        """Load golden test cases."""
        cases = []
        
        if not self.golden_cases_dir.exists():
            logger.warning(f"Golden cases directory not found: {self.golden_cases_dir}")
            return cases
        
        for file_path in self.golden_cases_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    case = json.load(f)
                    cases.append(case)
            except Exception as e:
                logger.error(f"Error loading golden case {file_path}: {e}")
        
        logger.info(f"Loaded {len(cases)} golden cases")
        return cases
    
    def evaluate_all(self) -> Dict:
        """Evaluate triage on all golden cases."""
        golden_cases = self.load_golden_cases()
        
        if not golden_cases:
            return {"error": "No golden cases found"}
        
        results = []
        severity_actual = []
        severity_predicted = []
        category_actual = []
        category_predicted = []
        
        for case in golden_cases:
            logger.info(f"Evaluating case: {case['incident_id']}")
            
            # Build incident context - merge top-level fields with alert_data
            alert_dict = {
                "incident_id": case["incident_id"],
                "timestamp": case["timestamp"],
                "alert_name": case["alert_name"],
                **case["alert_data"]
            }
            incident = IncidentContext(
                alert=IncidentAlert(**alert_dict),
                logs=case.get("logs", "")
            )
            
            # Perform triage
            triage_result = self.orchestrator.triage_incident(incident)
            
            # Compare with ground truth
            ground_truth = case["ground_truth"]
            
            evaluation = {
                "incident_id": case["incident_id"],
                "severity_match": triage_result.severity == ground_truth["severity"],
                "category_match": triage_result.category == ground_truth["category"],
                "processing_time": triage_result.processing_time,
                "predicted_severity": triage_result.severity,
                "actual_severity": ground_truth["severity"],
                "predicted_category": triage_result.category,
                "actual_category": ground_truth["category"],
                "root_cause_overlap": self._calculate_overlap(
                    triage_result.root_causes,
                    ground_truth["root_causes"]
                )
            }
            
            results.append(evaluation)
            severity_actual.append(ground_truth["severity"])
            severity_predicted.append(triage_result.severity)
            category_actual.append(ground_truth["category"])
            category_predicted.append(triage_result.category)
        
        # Calculate aggregate metrics
        severity_accuracy = sum(1 for r in results if r["severity_match"]) / len(results)
        category_accuracy = sum(1 for r in results if r["category_match"]) / len(results)
        avg_processing_time = sum(r["processing_time"] for r in results) / len(results)
        avg_root_cause_overlap = sum(r["root_cause_overlap"] for r in results) / len(results)
        
        summary = {
            "total_cases": len(results),
            "severity_accuracy": severity_accuracy,
            "category_accuracy": category_accuracy,
            "avg_processing_time": avg_processing_time,
            "avg_root_cause_precision": avg_root_cause_overlap,
            "individual_results": results
        }
        
        logger.info(f"Evaluation complete: {severity_accuracy:.1%} severity accuracy, {category_accuracy:.1%} category accuracy")
        return summary
    
    def _calculate_overlap(self, predicted: List[str], actual: List[str]) -> float:
        """Calculate overlap/precision between predicted and actual root causes."""
        if not predicted or not actual:
            return 0.0
        
        # Convert to lowercase for comparison
        predicted_lower = [p.lower() for p in predicted]
        actual_lower = [a.lower() for a in actual]
        
        # Calculate how many predicted causes appear in actual (precision-like)
        matches = sum(
            1 for p in predicted_lower
            if any(a in p or p in a for a in actual_lower)
        )
        
        return matches / len(predicted) if predicted else 0.0
    
    def generate_report(self, output_path: str = "data/evaluation_report.json"):
        """Generate and save evaluation report."""
        summary = self.evaluate_all()
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Evaluation report saved to: {output_path}")
        return summary
