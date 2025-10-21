# EpiWatch API - Remote Deployment Guide

## 🚀 **Easiest Options for Remote Access**

Your friend needs to access your API remotely. Here are the **3 best free solutions**:

---

## **Option 1: Render.com (FREE - Recommended)** ⭐

### Why Render?
- ✅ **100% Free tier** (750 hours/month)
- ✅ Automatic HTTPS
- ✅ Easy deployment from GitHub
- ✅ Your friend gets URL like: `https://epiwatch-api.onrender.com`

### Steps:

1. **Create GitHub Repository (if not already)**
   ```powershell
   cd C:\Users\Bruger\OneDrive\Desktop\NLP\epi-watch\epiwatch
   git init
   git add .
   git commit -m "Initial commit - EpiWatch API"
   ```

2. **Push to GitHub**
   - Create new repo on GitHub: https://github.com/new
   - Name it: `epiwatch-api`
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/epiwatch-api.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy on Render**
   - Go to: https://render.com (Sign up free)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect Python
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

4. **Get Your API URL**
   - After deployment: `https://epiwatch-api.onrender.com`
   - Share this with your friend!

**API Endpoints for your friend:**
```
https://epiwatch-api.onrender.com/api/v1/health
https://epiwatch-api.onrender.com/api/v1/alerts
https://epiwatch-api.onrender.com/api/v1/map
https://epiwatch-api.onrender.com/api/v1/trends
https://epiwatch-api.onrender.com/api/v1/statistics
```

---

## **Option 2: ngrok (Instant - For Quick Testing)** 🚀

### Why ngrok?
- ✅ **Instant** - Works in 2 minutes
- ✅ Creates public URL immediately
- ✅ Free tier available
- ⚠️ URL changes when you restart (unless you pay)

### Steps:

1. **Download ngrok**
   - Go to: https://ngrok.com/download
   - Download Windows version
   - Extract to a folder

2. **Run your API locally**
   ```powershell
   cd C:\Users\Bruger\OneDrive\Desktop\NLP\epi-watch\epiwatch
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

3. **In another terminal, run ngrok**
   ```powershell
   cd path\to\ngrok
   .\ngrok http 8000
   ```

4. **Get Public URL**
   - ngrok will show: `Forwarding: https://abc123.ngrok-free.app → http://localhost:8000`
   - Share `https://abc123.ngrok-free.app` with your friend!

**Pros:** Instant setup  
**Cons:** Must keep your computer running, URL changes on restart

---

## **Option 3: Railway.app (FREE - Alternative to Render)** 🚂

### Why Railway?
- ✅ $5 free credit monthly
- ✅ Easy GitHub integration
- ✅ Auto-deploy on git push

### Steps:

1. **Push to GitHub** (same as Render option)

2. **Deploy on Railway**
   - Go to: https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repo
   - Add environment variables if needed
   - Railway auto-detects Python and deploys

3. **Get Your URL**
   - Railway provides: `https://epiwatch-api.up.railway.app`
   - Share with your friend!

---

## **Option 4: Vercel (Serverless - Already Configured!)** ⚡

I see you already have `vercel.json` in your backend folder!

### Steps:

1. **Install Vercel CLI**
   ```powershell
   npm install -g vercel
   ```

2. **Deploy**
   ```powershell
   cd C:\Users\Bruger\OneDrive\Desktop\NLP\epi-watch\epiwatch\backend
   vercel
   ```

3. **Follow prompts**
   - Link to Vercel account
   - Deploy!

4. **Get URL**
   - Vercel gives you: `https://epiwatch-api.vercel.app`

---

## **Comparison Table**

| Service | Setup Time | Free Tier | Best For |
|---------|------------|-----------|----------|
| **Render** ⭐ | 10 min | 750 hrs/month | Production, permanent URL |
| **ngrok** | 2 min | Unlimited | Quick testing, temporary |
| **Railway** | 10 min | $5/month credit | Alternative to Render |
| **Vercel** | 5 min | Good limits | Serverless, fast deploy |

---

## **My Recommendation for You** 🎯

### **For Immediate Testing (Today):**
→ Use **ngrok** - Takes 2 minutes!

### **For Long-term Development:**
→ Use **Render** or **Railway** - Free & permanent URL

---

## **Quick Start: ngrok (Fastest Way)**

1. **Download:** https://ngrok.com/download
2. **Extract** the zip file
3. **Run your API:**
   ```powershell
   cd C:\Users\Bruger\OneDrive\Desktop\NLP\epi-watch\epiwatch
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
4. **In new terminal:**
   ```powershell
   cd path\to\ngrok
   .\ngrok http 8000
   ```
5. **Copy the HTTPS URL** (like `https://abc123.ngrok-free.app`)
6. **Send to your friend!**

He can then use it in his mobile app:
```kotlin
const val BASE_URL = "https://abc123.ngrok-free.app"
```

---

## **Need Help?**

Let me know which option you prefer, and I'll help you set it up! 🚀
