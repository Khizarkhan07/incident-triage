"""Test script to verify the triage copilot setup."""

import json
from pathlib import Path
from src.models import IncidentContext, IncidentAlert
from src.llm.ollama_client import OllamaClient
from src.storage.runbook_store import RunbookStore
from src.orchestrator import TriageOrchestrator
from src.utils.metrics import MetricsTracker
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_basic_components():
    """Test basic component initialization."""
    print("🧪 Testing basic components...")
    
    # Test LLM client
    print("  1. Testing LLM client...")
    llm = OllamaClient(model="llama3.2")
    if not llm.is_available():
        print("     ⚠️  Ollama not available. Please run: ollama pull llama3.2")
        return False
    print("     ✅ LLM client OK")
    
    # Test runbook store
    print("  2. Testing runbook store...")
    runbook_store = RunbookStore(runbooks_dir="data/runbooks")
    runbook_store.index_runbooks()
    runbooks = runbook_store.list_all_runbooks()
    print(f"     ✅ Indexed {len(runbooks)} runbooks")
    
    # Test metrics tracker
    print("  3. Testing metrics tracker...")
    metrics = MetricsTracker()
    print("     ✅ Metrics tracker OK")
    
    return llm, runbook_store, metrics


def test_triage():
    """Test end-to-end triage."""
    print("\n🧪 Testing end-to-end triage...")
    
    # Initialize components
    llm, runbook_store, metrics = test_basic_components()
    if not llm:
        return
    
    # Create orchestrator
    print("\n  4. Creating orchestrator...")
    orchestrator = TriageOrchestrator(
        llm_client=llm,
        runbook_store=runbook_store,
        metrics_tracker=metrics
    )
    print("     ✅ Orchestrator created")
    
    # Load a sample incident
    print("\n  5. Loading sample incident...")
    sample_file = Path("data/incidents/inc_001_db_pool.json")
    if not sample_file.exists():
        print("     ❌ Sample incident not found")
        return
    
    with open(sample_file, 'r') as f:
        incident_data = json.load(f)
    
    # Load corresponding logs
    log_file = Path("data/logs/inc_001_db_pool.log")
    if log_file.exists():
        with open(log_file, 'r') as f:
            logs = f.read()
    else:
        logs = None
    
    # Create incident context
    incident = IncidentContext(
        alert=IncidentAlert(**incident_data),
        logs=logs
    )
    print(f"     ✅ Loaded incident: {incident.alert.incident_id}")
    
    # Perform triage
    print("\n  6. Performing triage...")
    print("     This may take 30-60 seconds...")
    
    result = orchestrator.triage_incident(incident)
    
    print(f"\n✅ Triage completed in {result.processing_time:.2f}s")
    print(f"\n📊 Results:")
    print(f"   Severity: {result.severity}")
    print(f"   Category: {result.category}")
    print(f"   Confidence: {result.confidence_score:.0%}")
    print(f"   Root Causes: {len(result.root_causes)}")
    for i, cause in enumerate(result.root_causes, 1):
        print(f"      {i}. {cause}")
    print(f"   Relevant Runbooks: {len(result.relevant_runbooks)}")
    for rb in result.relevant_runbooks:
        print(f"      - {rb['title']} ({rb['similarity']:.0%} match)")
    
    return True


def test_evaluation():
    """Test evaluation on golden cases."""
    print("\n🧪 Testing evaluation...")
    
    from src.evaluation.evaluator import TriageEvaluator
    
    # Initialize components
    llm, runbook_store, metrics = test_basic_components()
    if not llm:
        return
    
    orchestrator = TriageOrchestrator(
        llm_client=llm,
        runbook_store=runbook_store,
        metrics_tracker=metrics
    )
    
    evaluator = TriageEvaluator(
        orchestrator=orchestrator,
        golden_cases_dir="data/golden_cases"
    )
    
    print("\n  Running evaluation (this will take a few minutes)...")
    summary = evaluator.evaluate_all()
    
    if "error" in summary:
        print(f"     ❌ {summary['error']}")
        return
    
    print(f"\n✅ Evaluation completed")
    print(f"\n📊 Summary:")
    print(f"   Total Cases: {summary['total_cases']}")
    print(f"   Severity Accuracy: {summary['severity_accuracy']:.1%}")
    print(f"   Category Accuracy: {summary['category_accuracy']:.1%}")
    print(f"   Avg Processing Time: {summary['avg_processing_time']:.2f}s")
    print(f"   Avg Root Cause Precision: {summary['avg_root_cause_precision']:.1%}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚨 Incident Triage Copilot - Test Suite")
    print("=" * 60)
    
    try:
        # Test basic triage
        if test_triage():
            print("\n" + "=" * 60)
            print("✅ All basic tests passed!")
            print("=" * 60)
            
            # Ask if user wants to run evaluation
            response = input("\nRun full evaluation? (y/n): ")
            if response.lower() == 'y':
                test_evaluation()
        
        print("\n✨ Testing complete! Run the app with: streamlit run app.py")
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
