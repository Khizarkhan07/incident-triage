# 🚀 Quick Start Guide

## Prerequisites Check

✅ Python 3.8+ installed  
✅ Ollama installed (already found at `/usr/local/bin/ollama`)  
✅ macOS environment  

## Installation (5 minutes)

### Step 1: Navigate to Project
```bash
cd /Users/khizar.khan/gen-ai/incident-triage-copilot
```

### Step 2: Run Setup Script
```bash
./setup.sh
```

This will:
- Create virtual environment
- Install Python dependencies
- Pull Llama 3.2 model (~2GB download)
- Start Ollama server
- Index runbooks

### Step 3: Test Installation
```bash
source venv/bin/activate
python test_copilot.py
```

Expected output: Should run a complete triage on sample incident in ~30-60 seconds.

### Step 4: Launch the App
```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## First-Time Usage

### 1. Try a Sample Incident
- Navigate to "🆕 New Incident" tab
- Select "INC-2026-001" from the dropdown
- Click "🔍 Analyze Incident"
- Wait ~30s for results

### 2. Review Results
You'll see:
- **Classification:** Severity (SEV1-4) & Category
- **Root Causes:** Ranked by likelihood
- **Mitigation Plan:** Step-by-step actions with commands
- **Runbook Citations:** Relevant documentation

### 3. Explore Features
- **📊 Evaluate:** Run on golden test cases
- **📚 Runbooks:** Browse/search knowledge base
- **📈 Metrics:** View performance stats

---

## Troubleshooting

### Issue: Ollama model not found
```bash
ollama pull llama3.2
```

### Issue: Ollama not running
```bash
ollama serve
```
(Run in separate terminal)

### Issue: Port 8501 already in use
```bash
streamlit run app.py --server.port 8502
```

### Issue: SQLite/dependencies error
```bash
pip install --upgrade -r requirements.txt
```

---

## Testing the System

### Quick Test (30 seconds)
```bash
python test_copilot.py
```

### Full Evaluation (2-3 minutes)
In the app:
1. Go to "📊 Evaluate" tab
2. Click "🚀 Run Evaluation"
3. View accuracy metrics

---

## What to Expect

### Performance Benchmarks
- **Classification Time:** ~5-10s
- **Root Cause Analysis:** ~10-15s
- **Mitigation Plan:** ~10-15s
- **Total Triage Time:** ~25-40s

### Accuracy (on golden cases)
- **Severity Accuracy:** 80-90%
- **Category Accuracy:** 85-95%
- **Root Cause Precision:** 70-80%

---

## Next Steps

### 1. Add Your Own Incidents
Create JSON files in `data/incidents/`:
```json
{
  "incident_id": "INC-YYYY-XXX",
  "timestamp": "2026-02-17T12:00:00Z",
  "alert_name": "Your Alert",
  "description": "Description",
  "metrics": {},
  "affected_services": [],
  "environment": "production",
  "tags": []
}
```

### 2. Add Custom Runbooks
Create markdown files in `data/runbooks/`:
```markdown
# Your Runbook Title

## Root Causes
- Cause 1
- Cause 2

## Immediate Mitigation
### Step 1: ...
```

### 3. Train with Feedback
After each triage:
1. Provide actual severity/category
2. Rate root cause accuracy
3. Mark if mitigation was helpful
4. System learns from feedback

---

## Development Mode

### Running Tests
```bash
python -m pytest tests/  # (if you add tests)
```

### Viewing Logs
```bash
tail -f data/copilot.log
```

### Monitoring Ollama
```bash
ollama list  # Show installed models
ollama ps    # Show running models
```

---

## Configuration

Edit `config.yaml` to customize:
- LLM model (try `qwen2.5`, `mistral`, etc.)
- Temperature (0.0-1.0)
- Number of runbooks retrieved
- Severity levels
- Categories

---

## Stopping the System

### Stop Streamlit
`Ctrl+C` in the terminal

### Stop Ollama (optional)
```bash
pkill ollama
```

---

## Getting Help

- Check logs: `data/copilot.log`
- Review README.md
- Check PRESENTATION.md for architecture details

---

## Ready to Share!

Once tested:
1. Take screenshots of results
2. Record a demo video
3. Share in #gen-ai Slack channel
4. Present at team meeting

**Have fun triaging! 🚨**
