# Quick Start Guide

## ✅ What's Been Done

Your Incident Triage Copilot is now **ready for cloud deployment**! Here's what was added:

1. ✅ **Groq client** - Cloud LLM integration
2. ✅ **Dual provider support** - Switch between Ollama (local) and Groq (cloud)
3. ✅ **Secrets management** - Secure API key handling
4. ✅ **Deployment docs** - Step-by-step Streamlit Cloud guide

## 🚀 Next Steps

### Option 1: Test Locally with Groq

```bash
# 1. Add your Groq API key
# Edit .streamlit/secrets.toml and paste your key:
GROQ_API_KEY = "gsk_your_actual_key_here"

# 2. Already done - config.yaml is set to "groq"
# 3. Already done - groq package installed

# 4. Run the app
streamlit run app.py

# You should see: "✅ Using Groq: llama-3.1-8b-instant"
```

### Option 2: Deploy to Streamlit Cloud (Public Demo)

**See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions**

Quick version:
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Create new app from your repo
4. Add `GROQ_API_KEY` in Advanced Settings → Secrets
5. Deploy!

## 📝 Files Added/Modified

**New files:**
- `src/llm/groq_client.py` - Groq API client
- `.streamlit/secrets.toml` - Your API key (not committed)
- `.streamlit/secrets.toml.example` - Template for others
- `DEPLOYMENT.md` - Full deployment guide
- `QUICKSTART_DEPLOY.md` - This file

**Modified files:**
- `app.py` - Added provider switching logic
- `config.yaml` - Changed to `provider: "groq"`
- `requirements.txt` - Added `groq>=0.4.0`
- `README.md` - Mentioned cloud deployment

## 🔄 Switching Between Providers

### Use Groq (Cloud, for demos)
```yaml
# config.yaml
llm:
  provider: "groq"
  model: "llama-3.1-8b-instant"
```

### Use Ollama (Local, for development)
```yaml
# config.yaml
llm:
  provider: "ollama"
  model: "llama3.1:8b"
```

## 🎯 Key Features

**With Groq:**
- ✅ Fast inference (~2-3s per request)
- ✅ No local setup needed
- ✅ 14,400 free requests/day
- ✅ Works on any machine
- ⚠️ Data sent to cloud

**With Ollama:**
- ✅ 100% local/private
- ✅ No API limits
- ✅ Works offline
- ⚠️ Requires 5GB+ RAM
- ⚠️ Slower inference (~10-15s)

## 🐛 Troubleshooting

**"GROQ_API_KEY not found"**
- Check `.streamlit/secrets.toml` has your key
- Format: `GROQ_API_KEY = "gsk_..."`

**"Module 'groq' not found"**
```bash
uv pip install groq
```

**Want to switch back to Ollama?**
```bash
# 1. Edit config.yaml - change provider to "ollama"
# 2. Restart app
streamlit run app.py
```

## 📊 Performance Comparison

| Feature | Ollama (Local) | Groq (Cloud) |
|---------|---------------|--------------|
| Speed | 10-15s/incident | 3-5s/incident |
| Cost | Free | Free (14.4K/day) |
| Privacy | 100% local | Cloud API |
| Setup | Install Ollama | API key only |
| RAM needed | 5GB+ | <500MB |

## 🎉 You're Ready!

Your app is now configured for cloud deployment. When you're ready:
1. Get your Groq API key from [console.groq.com](https://console.groq.com)
2. Add it to `.streamlit/secrets.toml`
3. Test locally
4. Push to GitHub
5. Deploy to Streamlit Cloud

Questions? Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions!
