# 🚀 Deploying to Streamlit Cloud

This guide walks you through deploying the Incident Triage Copilot to Streamlit Cloud using Groq for free cloud-based LLM inference.

## Prerequisites

- [ ] GitHub account
- [ ] Groq API key (get free at [console.groq.com](https://console.groq.com))
- [ ] Code pushed to GitHub repository

## Step 1: Get Your Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `gsk_...`)

**Free Tier Limits:**
- 14,400 requests/day
- 30 requests/minute
- More than enough for demos!

## Step 2: Test Locally with Groq

Before deploying, test that Groq works locally:

```bash
# 1. Install groq package
cd /Users/khizar.khan/gen-ai/incident-triage-copilot
uv pip install groq

# 2. Add your API key to secrets.toml
# Edit .streamlit/secrets.toml and replace the placeholder:
GROQ_API_KEY = "gsk_your_actual_key_here"

# 3. Verify config.yaml is set to groq
# Should say: provider: "groq"

# 4. Run locally
streamlit run app.py
```

You should see "✅ Using Groq: llama-3.1-8b-instant" in the sidebar.

## Step 3: Push to GitHub

```bash
# Make sure all changes are committed
git add .
git commit -m "Add Groq support for cloud deployment"
git push origin main
```

## Step 4: Deploy to Streamlit Cloud

### 4.1 Go to Streamlit Cloud

1. Visit [https://share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit access to your GitHub

### 4.2 Create New App

1. Click **"New app"** button
2. Fill in:
   - **Repository**: Select your repo (e.g., `yourusername/incident-triage-copilot`)
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (e.g., `incident-triage-demo`)

### 4.3 Add Secrets

**CRITICAL STEP:** Before deploying, add your API key:

1. Click **"Advanced settings"** (before deploying)
2. In the **Secrets** section, paste:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_key_here"
   ```
3. Click **"Save"**

### 4.4 Deploy!

1. Click **"Deploy!"**
2. Wait 2-3 minutes for initial deployment
3. Your app will be live at: `https://yourapp.streamlit.app`

## Step 5: Verify Deployment

Once deployed:

1. Open your app URL
2. Check sidebar - should show "✅ Using Groq: llama-3.1-8b-instant"
3. Test with a sample incident (INC-2026-001)
4. Verify triage completes successfully

## Troubleshooting

### "GROQ_API_KEY not found"
- Go to Streamlit Cloud dashboard
- Click the ⋮ menu → **Settings** → **Secrets**
- Add `GROQ_API_KEY = "your-key"`
- Click **Save** and **Reboot app**

### "Module 'groq' not found"
- Verify `requirements.txt` includes `groq>=0.4.0`
- Trigger rebuild: make any small change and push to GitHub

### App crashes or times out
- Check **Logs** in Streamlit Cloud dashboard
- Groq free tier: 14,400 req/day, 30 req/min
- May hit rate limits during eval (runs 3 incidents back-to-back)

### Want to switch back to Ollama locally?
```yaml
# In config.yaml, change:
llm:
  provider: "ollama"  # Change back from "groq"
  model: "llama3.1:8b"  # Local Ollama model
```

## Managing Your Deployment

### Update App
```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main
# Streamlit Cloud auto-deploys in ~30 seconds
```

### View Logs
- Go to Streamlit Cloud dashboard
- Click your app → **Logs** tab
- See real-time errors and debugging info

### Pause/Delete App
- Dashboard → ⋮ menu → **Settings**
- **Pause app** (saves resources)
- **Delete app** (permanent removal)

## Cost & Limits

**Streamlit Cloud (Free Tier):**
- ✅ 1 private app
- ✅ Unlimited public apps
- ✅ 1 GB RAM
- ✅ 1 vCPU
- ⚠️ Apps sleep after 7 days of inactivity

**Groq (Free Tier):**
- ✅ 14,400 requests/day
- ✅ 30 requests/minute
- ✅ llama-3.1-8b-instant model
- ⚠️ Rate limits apply

**Estimated usage:**
- 1 incident triage = ~4 API calls
- 100 triages/day = well within free tier

## Next Steps

1. **Share your demo!** Send the URL to colleagues
2. **Add more runbooks** to improve accuracy
3. **Tune prompts** based on real incident data
4. **Monitor usage** in Groq console

## Security Notes

⚠️ **Never commit secrets:**
- `.streamlit/secrets.toml` is in `.gitignore`
- Use Streamlit Cloud secrets for deployment
- Rotate API keys if accidentally exposed

🔒 **Data privacy:**
- With Groq, incident data is sent to cloud (encrypted in transit)
- For sensitive data, use local Ollama deployment instead
- Review Groq's privacy policy: [groq.com/privacy](https://groq.com/privacy)

---

## Support

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Groq Docs**: [console.groq.com/docs](https://console.groq.com/docs)
- **Issues**: Open on GitHub repo

Happy deploying! 🚀
