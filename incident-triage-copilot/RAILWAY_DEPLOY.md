# Railway Deployment Guide

## Quick Deploy to Railway

1. **Sign up at Railway**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `incident-triage` repository

3. **Configure Settings**
   Railway will auto-detect the Procfile. Add environment variables:
   
   - Click **Variables** tab
   - Add: `GROQ_API_KEY` = `your-groq-key-here`
   - Add: `PORT` = `8501` (optional, Railway sets this)

4. **Deploy**
   - Railway auto-deploys on git push
   - Initial build: ~10 minutes
   - Subsequent: ~3 minutes

5. **Access Your App**
   - Railway provides URL: `https://yourapp.up.railway.app`
   - Click "Generate Domain" if not auto-generated

## Railway Advantages

✅ **Better for ML apps** - More RAM (8GB vs 1GB)
✅ **Faster builds** - Better infrastructure
✅ **Free tier** - $5 credit/month (enough for demos)
✅ **Auto-scaling** - Handles traffic better
✅ **Better logging** - See build progress clearly

## Monitoring

- **Logs**: Railway dashboard → Deployments → Logs
- **Metrics**: See RAM/CPU usage in real-time
- **Restarts**: Auto-restart on crashes

## Cost

**Free Tier:**
- $5 credit/month
- ~100 hours runtime (light usage)
- Enough for demos/testing

**After free tier:**
- ~$0.20/day for active app
- Sleep after inactivity (saves credits)

## Deploy!

```bash
# Push changes
git add Procfile
git commit -m "Add Railway deployment config"
git push origin main

# Then deploy on Railway dashboard
```
