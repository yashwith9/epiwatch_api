# Deploy EpiWatch API to Render.com (FREE & PERMANENT!)

## ✅ Files Ready to Deploy:
- ✅ main.py (your API)
- ✅ requirements.txt (Python packages)
- ✅ Procfile (startup command)
- ✅ results/ folder (your data)

---

## 🚀 DEPLOYMENT STEPS (10 Minutes)

### Step 1: Create Render Account (2 minutes)
1. Go to: https://render.com/
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest) or Email
4. Verify your email

### Step 2: Upload to GitHub (5 minutes)

**Option A: Use GitHub Desktop (Easiest)**
1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in with your GitHub account
3. Click "Add" → "Add Existing Repository"
4. Select: `C:\Users\Bruger\OneDrive\Desktop\NLP\epiwatch\backend`
5. Click "Publish repository"
6. Name it: `epiwatch-api`
7. Click "Publish repository"

**Option B: Use Command Line**
```powershell
cd C:\Users\Bruger\OneDrive\Desktop\NLP\epiwatch\backend

# Initialize git
git init
git add .
git commit -m "Deploy EpiWatch API"

# Create repo on GitHub and push
# (You'll need to create a repo on github.com first)
git remote add origin https://github.com/YOUR_USERNAME/epiwatch-api.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render (3 minutes)
1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect account"** to connect GitHub
4. Select your `epiwatch-api` repository
5. Configure:
   - **Name:** `epiwatch-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Select **"Free"** (it's free forever!)
6. Click **"Create Web Service"**

### Step 4: Wait for Deployment (2-3 minutes)
- Render will automatically:
  - Install your dependencies
  - Start your FastAPI server
  - Give you a public URL!

### Step 5: Get Your Public URL! 🎉
You'll get a URL like:
```
https://epiwatch-api.onrender.com
```

**This URL is:**
- ✅ Permanent (doesn't change)
- ✅ Free forever
- ✅ HTTPS included
- ✅ No passwords needed
- ✅ Works 24/7 (even when your laptop is off!)

---

## 🌐 SHARE WITH YOUR FRIEND

Send your friend these URLs:

**API Documentation:**
```
https://epiwatch-api.onrender.com/docs
```

**Endpoints:**
- Statistics: `https://epiwatch-api.onrender.com/api/v1/statistics`
- Map: `https://epiwatch-api.onrender.com/api/v1/map`
- Trends: `https://epiwatch-api.onrender.com/api/v1/trends`
- Alerts: `https://epiwatch-api.onrender.com/api/v1/alerts`

---

## 📝 IMPORTANT NOTES

1. **Free Tier Limitations:**
   - Your API will "sleep" after 15 minutes of no requests
   - First request after sleeping takes ~30 seconds to wake up
   - After that, it's fast!
   - To keep it awake 24/7, upgrade to paid ($7/month) or use a ping service

2. **Updates:**
   - To update your API, just push to GitHub
   - Render auto-deploys new changes!

3. **Monitoring:**
   - Check logs at: https://dashboard.render.com/
   - See metrics, errors, and deployment status

---

## 🔄 ALTERNATIVE: Even Faster Options

### Option 1: Vercel (2 minutes, no GitHub needed!)
1. Install Vercel CLI: `npm install -g vercel`
2. Deploy: `cd backend && vercel`
3. Done! You get a URL instantly

### Option 2: Railway (Similar to Render)
1. Go to: https://railway.app/
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Done!

---

## ✨ COMPARISON

| Service | Setup Time | Free? | Permanent? | HTTPS? |
|---------|-----------|-------|------------|--------|
| **Render** | 10 min | ✅ Yes | ✅ Yes | ✅ Yes |
| **Vercel** | 2 min | ✅ Yes | ✅ Yes | ✅ Yes |
| **Railway** | 10 min | ✅ $5 credit | ✅ Yes | ✅ Yes |
| LocalTunnel | 1 min | ✅ Yes | ❌ No | ✅ Yes |
| ngrok | 5 min | ✅ Yes | ❌ No | ✅ Yes |

---

## 🎯 MY RECOMMENDATION

**Use Render** - It's:
- Free forever
- Permanent URL
- Auto-deploys on push
- No password screens
- Professional solution

---

## 🆘 NEED HELP?

If you get stuck at any step, let me know which step and I'll help you!
