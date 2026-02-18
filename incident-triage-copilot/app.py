"""Streamlit UI for Incident Triage Copilot."""

import streamlit as st
import yaml
import json
from pathlib import Path
import time
import os
import sys

# Get the directory where app.py is located
APP_DIR = Path(__file__).parent.absolute()
os.chdir(APP_DIR)

# Add the project root to Python path
sys.path.insert(0, str(APP_DIR))

from src.llm.ollama_client import OllamaClient
from src.storage.runbook_store import RunbookStore
from src.orchestrator import TriageOrchestrator
from src.evaluation.evaluator import TriageEvaluator
from src.models import IncidentContext, IncidentAlert
from src.utils.metrics import MetricsTracker
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Page config
st.set_page_config(
    page_title="🚨 Incident Triage Copilot",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load config
@st.cache_resource
def load_config():
    config_path = APP_DIR / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize components
@st.cache_resource
def init_components():
    """Initialize all system components."""
    
    # LLM Client
    llm = OllamaClient(
        model=config["llm"]["model"],
        base_url=config["llm"]["base_url"],
        temperature=config["llm"]["temperature"],
        max_tokens=config["llm"]["max_tokens"]
    )
    
    # Check if Ollama is available
    if not llm.is_available():
        st.error("⚠️ Ollama is not running or model not available. Please run: `ollama pull llama3.2`")
        st.stop()
    
    # Runbook Store
    runbook_store = RunbookStore(
        runbooks_dir=config["storage"]["runbooks_dir"]
    )
    
    # Index runbooks
    runbook_store.index_runbooks()
    
    # Metrics Tracker
    metrics = MetricsTracker(
        feedback_file=config["storage"]["feedback_file"]
    )
    
    # Orchestrator
    orchestrator = TriageOrchestrator(
        llm_client=llm,
        runbook_store=runbook_store,
        metrics_tracker=metrics
    )
    
    # Evaluator
    evaluator = TriageEvaluator(
        orchestrator=orchestrator,
        golden_cases_dir=config["storage"]["golden_cases_dir"]
    )
    
    return orchestrator, runbook_store, metrics, evaluator

try:
    orchestrator, runbook_store, metrics, evaluator = init_components()
except Exception as e:
    st.error(f"Failed to initialize components: {e}")
    st.info("Make sure Ollama is running: `brew install ollama && ollama serve`")
    st.stop()

# Sidebar
st.sidebar.title("🚨 Incident Triage Copilot")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🆕 New Incident", "📊 Evaluate", "📚 Runbooks", "📈 Metrics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ System Status")
st.sidebar.success(f"✅ LLM: {config['llm']['model']}")
st.sidebar.info(f"📖 Runbooks: {len(runbook_store.list_all_runbooks())} indexed")

# Main content
if page == "🆕 New Incident":
    st.title("🚨 Incident Triage Copilot")
    st.markdown("Submit an incident alert to get AI-powered triage with root cause analysis and mitigation plans.")
    
    # Load sample incidents for quick testing
    sample_incidents_dir = Path(config["storage"]["incidents_dir"])
    sample_incidents = {}
    if sample_incidents_dir.exists():
        for file_path in sample_incidents_dir.glob("*.json"):
            with open(file_path, 'r') as f:
                incident_data = json.load(f)
                sample_incidents[incident_data["incident_id"]] = incident_data
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Incident Details")
        
        # Sample selector
        if sample_incidents:
            sample_choice = st.selectbox(
                "Load Sample Incident",
                ["-- Custom --"] + list(sample_incidents.keys())
            )
        else:
            sample_choice = "-- Custom --"
        
        if sample_choice != "-- Custom --":
            sample_data = sample_incidents[sample_choice]
            default_alert = json.dumps(sample_data, indent=2)
            
            # Load corresponding logs
            log_file = Path(config["storage"]["logs_dir"]) / f"{Path(sample_data['incident_id']).stem.replace('INC', 'inc')}_*.log"
            log_files = list(Path(config["storage"]["logs_dir"]).glob(log_file.name.replace('*', '*')))
            if log_files:
                with open(log_files[0], 'r') as f:
                    default_logs = f.read()
            else:
                default_logs = ""
        else:
            default_alert = """{
  "incident_id": "INC-2026-XXX",
  "timestamp": "2026-02-17T12:00:00Z",
  "source": "Monitoring System",
  "alert_name": "Alert Name",
  "description": "Alert description",
  "metrics": {},
  "affected_services": [],
  "environment": "production",
  "tags": []
}"""
            default_logs = ""
        
        alert_json = st.text_area(
            "Incident Alert (JSON)",
            value=default_alert,
            height=250,
            help="Paste the incident alert JSON"
        )
        
        logs_text = st.text_area(
            "Recent Logs (Optional)",
            value=default_logs,
            height=150,
            help="Paste relevant log entries"
        )
        
        additional_context = st.text_area(
            "Additional Context (Optional)",
            height=100,
            help="Any additional information about the incident"
        )
        
        triage_button = st.button("🔍 Analyze Incident", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("ℹ️ How It Works")
        st.markdown("""
        1. **Classify**: Severity & Category
        2. **Analyze**: Root Cause Analysis
        3. **Plan**: Mitigation Steps
        4. **Cite**: Relevant Runbooks
        
        **Powered by:**
        - 🤖 Local LLM (Ollama)
        - 📚 Vector Search
        - 📖 Runbook Library
        """)
    
    # Triage execution
    if triage_button:
        try:
            # Parse alert JSON
            alert_data = json.loads(alert_json)
            
            # Create incident context
            incident = IncidentContext(
                alert=IncidentAlert(**alert_data),
                logs=logs_text if logs_text else None,
                additional_context=additional_context if additional_context else None
            )
            
            # Show progress
            with st.spinner("🔍 Analyzing incident..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Step 1/3: Classifying incident...")
                progress_bar.progress(33)
                
                # Perform triage
                result = orchestrator.triage_incident(incident)
                
                status_text.text("Step 2/3: Analyzing root causes...")
                progress_bar.progress(66)
                time.sleep(0.5)
                
                status_text.text("Step 3/3: Generating mitigation plan...")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                progress_bar.empty()
                status_text.empty()
            
            # Display results
            st.success(f"✅ Triage completed in {result.processing_time:.2f}s")
            
            # Classification
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                severity_color = {
                    "SEV1": "🔴",
                    "SEV2": "🟠",
                    "SEV3": "🟡",
                    "SEV4": "🟢"
                }
                st.metric("Severity", f"{severity_color.get(result.severity, '⚪')} {result.severity}")
            with col2:
                st.metric("Category", result.category)
            with col3:
                st.metric("Confidence", f"{result.confidence_score:.0%}")
            
            # Root Causes
            st.markdown("### 🔍 Root Causes")
            for i, cause in enumerate(result.root_causes, 1):
                st.markdown(f"**{i}.** {cause}")
            
            if result.reasoning:
                with st.expander("💡 Reasoning"):
                    st.markdown(result.reasoning)
            
            # Mitigation Plan
            st.markdown("### 🛠️ Mitigation Plan")
            st.markdown(result.mitigation_plan)
            
            # Relevant Runbooks
            if result.relevant_runbooks:
                st.markdown("### 📚 Relevant Runbooks")
                for rb in result.relevant_runbooks:
                    with st.expander(f"📖 {rb['title']} (Similarity: {rb['similarity']:.0%})"):
                        content = runbook_store.get_runbook_by_path(rb['file_path'])
                        st.markdown(content)
            
            # Feedback
            st.markdown("---")
            st.markdown("### 📝 Feedback")
            with st.form("feedback_form"):
                st.markdown("Help improve the copilot by providing feedback:")
                
                col1, col2 = st.columns(2)
                with col1:
                    actual_severity = st.selectbox(
                        "Actual Severity",
                        config["triage"]["severity_levels"],
                        index=config["triage"]["severity_levels"].index(result.severity)
                    )
                    actual_category = st.selectbox(
                        "Actual Category",
                        config["triage"]["categories"],
                        index=config["triage"]["categories"].index(result.category) if result.category in config["triage"]["categories"] else 0
                    )
                with col2:
                    root_cause_accuracy = st.slider(
                        "Root Cause Accuracy",
                        0.0, 1.0, 0.7, 0.1,
                        help="How accurate were the identified root causes?"
                    )
                    mitigation_helpful = st.checkbox(
                        "Mitigation Plan Helpful",
                        value=True
                    )
                
                feedback_notes = st.text_area("Additional Notes")
                
                submit_feedback = st.form_submit_button("Submit Feedback")
                
                if submit_feedback:
                    metrics.record_feedback(
                        incident_id=result.incident_id,
                        severity_actual=actual_severity,
                        category_actual=actual_category,
                        root_cause_accuracy=root_cause_accuracy,
                        mitigation_helpful=mitigation_helpful,
                        notes=feedback_notes
                    )
                    st.success("✅ Thank you for your feedback!")
        
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
        except Exception as e:
            st.error(f"Error during triage: {e}")
            logger.error(f"Triage error: {e}", exc_info=True)

elif page == "📊 Evaluate":
    st.title("📊 Evaluation Dashboard")
    st.markdown("Evaluate the copilot's performance on golden test cases.")
    
    if st.button("🚀 Run Evaluation", type="primary"):
        with st.spinner("Running evaluation on golden cases..."):
            summary = evaluator.evaluate_all()
        
        if "error" in summary:
            st.error(summary["error"])
        else:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Severity Accuracy", f"{summary['severity_accuracy']:.1%}")
            with col2:
                st.metric("Category Accuracy", f"{summary['category_accuracy']:.1%}")
            with col3:
                st.metric("Avg Processing Time", f"{summary['avg_processing_time']:.2f}s")
            with col4:
                st.metric("Root Cause Precision", f"{summary['avg_root_cause_precision']:.1%}")
            
            # Individual results
            st.markdown("### 📋 Individual Results")
            for result in summary["individual_results"]:
                with st.expander(f"{result['incident_id']} - {'✅' if result['severity_match'] and result['category_match'] else '❌'}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Predicted:** {result['predicted_severity']} / {result['predicted_category']}")
                        st.markdown(f"**Actual:** {result['actual_severity']} / {result['actual_category']}")
                    with col2:
                        st.markdown(f"**Root Cause Overlap:** {result['root_cause_overlap']:.1%}")
                        st.markdown(f"**Processing Time:** {result['processing_time']:.2f}s")

elif page == "📚 Runbooks":
    st.title("📚 Runbook Library")
    st.markdown("Browse and search indexed runbooks.")
    
    search_query = st.text_input("🔍 Search Runbooks", placeholder="e.g., database connection issues")
    
    if search_query:
        results = runbook_store.search_runbooks(search_query, top_k=5)
        
        st.markdown(f"### Found {len(results)} relevant runbooks")
        
        for rb in results:
            with st.expander(f"📖 {rb['title']} (Similarity: {rb['similarity']:.0%})"):
                st.markdown(f"**Category:** {rb['category']}")
                st.markdown(f"**Path:** `{rb['file_path']}`")
                st.markdown("---")
                st.markdown(rb['content'])
    else:
        all_runbooks = runbook_store.list_all_runbooks()
        st.markdown(f"### All Runbooks ({len(all_runbooks)})")
        
        for rb in all_runbooks:
            with st.expander(f"📖 {rb['title']} - {rb['category']}"):
                st.markdown(f"**Path:** `{rb['file_path']}`")
                st.markdown("---")
                st.markdown(rb['content'])

elif page == "📈 Metrics":
    st.title("📈 Performance Metrics")
    st.markdown("View copilot performance metrics and feedback.")
    
    summary = metrics.get_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Triages", summary.get("total_triages", 0))
    with col2:
        st.metric("Avg Processing Time", summary.get("avg_processing_time", "N/A"))
    with col3:
        st.metric("Session Start", summary.get("session_start", "N/A")[:19])
    
    # Load feedback if available
    feedback_file = Path(config["storage"]["feedback_file"])
    if feedback_file.exists():
        st.markdown("### 📝 Recent Feedback")
        
        feedbacks = []
        with open(feedback_file, 'r') as f:
            for line in f:
                feedbacks.append(json.loads(line))
        
        if feedbacks:
            for fb in reversed(feedbacks[-10:]):  # Show last 10
                with st.expander(f"{fb['incident_id']} - {fb['timestamp'][:19]}"):
                    st.markdown(f"**Actual:** {fb['severity_actual']} / {fb['category_actual']}")
                    st.markdown(f"**Root Cause Accuracy:** {fb['root_cause_accuracy']:.0%}")
                    st.markdown(f"**Mitigation Helpful:** {'✅' if fb['mitigation_helpful'] else '❌'}")
                    if fb.get('notes'):
                        st.markdown(f"**Notes:** {fb['notes']}")
        else:
            st.info("No feedback recorded yet")
    else:
        st.info("No feedback data available")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
Built with ❤️ using Ollama, SQLite & Streamlit<br>
100% Local • 100% Free
</div>
""", unsafe_allow_html=True)
