# GenAI Incident Triage Copilot

An AI-powered assistant that helps triage production incidents by analyzing alerts, logs, and runbooks to:
- **Classify incidents** by severity and category
- **Suggest likely root causes** with evidence-based reasoning
- **Draft mitigation plans** with citations to relevant runbooks
- **Learn from feedback** through post-incident reviews
- **Track performance** via evaluation metrics

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │
┌────────▼────────┐
│  Triage Agent   │
│  - Classifier   │
│  - Root Cause   │
│  - Mitigation   │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    │         │         │          │
┌───▼───┐ ┌──▼──┐ ┌────▼────┐ ┌──▼───┐
│Ollama │ │Vec  │ │ Runbook │ │Eval  │
│ LLM   │ │Store│ │  Store  │ │Engine│
└───────┘ └─────┘ └─────────┘ └──────┘
```

## Local Stack (100% Free)

- **LLM**: Ollama (llama3.2, qwen2.5)
- **Vector DB**: SQLite + sqlite-vec
- **UI**: Streamlit
- **Observability**: Built-in logging + metrics
- **Data**: Local JSON/markdown files

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Ollama (if not already)
# macOS: brew install ollama
# Then: ollama pull llama3.2

# 3. Run the copilot
streamlit run app.py
```

## Project Structure

```
incident-triage-copilot/
├── app.py                      # Streamlit UI
├── requirements.txt
├── config.yaml                 # Configuration
├── data/
│   ├── incidents/              # Sample incident alerts
│   ├── logs/                   # Sample log files
│   ├── runbooks/               # Markdown runbooks
│   └── golden_cases/           # Evaluation dataset
├── src/
│   ├── agents/
│   │   ├── classifier.py       # Incident classifier
│   │   ├── root_cause.py       # Root cause analyzer
│   │   └── mitigation.py       # Mitigation planner
│   ├── storage/
│   │   ├── vector_store.py     # Vector DB operations
│   │   └── runbook_store.py    # Runbook retrieval
│   ├── llm/
│   │   └── ollama_client.py    # Ollama integration
│   ├── evaluation/
│   │   └── evaluator.py        # Evaluation engine
│   └── utils/
│       ├── logger.py
│       └── metrics.py
└── tests/
    └── test_triage.py
```

## Usage

1. **Submit Incident**: Paste alert JSON + relevant logs
2. **Get Triage**: AI classifies, analyzes, and suggests fixes
3. **Review & Act**: Follow mitigation steps with citations
4. **Provide Feedback**: Rate accuracy for continuous learning

## Evaluation Metrics

- **Classification Accuracy**: % correct severity/category
- **Root Cause Precision**: Overlap with actual RCA
- **Time-to-First-Action**: Seconds from alert to suggestion
- **Citation Quality**: % suggestions with valid runbook links

## Future Enhancements

- [ ] Multi-modal analysis (graphs, metrics)
- [ ] Slack/PagerDuty integration
- [ ] Real-time alert streaming
- [ ] Team collaboration features
