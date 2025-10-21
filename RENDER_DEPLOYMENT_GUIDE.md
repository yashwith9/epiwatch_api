# 🚀 Deploy EpiWatch API to Render - Step by Step Guide

## Prerequisites Check ✅

Before we start, let's make sure everything is ready.

---

## **Option A: Deploy via GitHub (Recommended)**

### Step 1: Install Git (if not installed)

1. Download Git for Windows: https://git-scm.com/download/win
2. Install with default settings
3. Restart your terminal

### Step 2: Create GitHub Account & Repository

1. Go to: https://github.com/signup
2. Create account (or login if you have one)
3. Create new repository:
   - Go to: https://github.com/new
   - Repository name: `epiwatch-api`
   - Description: `Disease Outbreak Detection API`
   - Select: **Public**
   - Click "Create repository"

### Step 3: Initialize Git & Push Code

Open PowerShell in your project folder:

```powershell
# Navigate to your project
cd C:\Users\Bruger\OneDrive\Desktop\NLP\epi-watch\epiwatch

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - EpiWatch API for Render deployment"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/epiwatch-api.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** You'll be asked for GitHub credentials. Use your:
- Username: Your GitHub username
- Password: Personal Access Token (not your password!)
  - Generate token at: https://github.com/settings/tokens
  - Select: `repo` scope
  - Copy the token

### Step 4: Deploy on Render

1. **Go to Render:** https://render.com
2. **Sign Up:** 
   - Click "Get Started for Free"
   - Sign up with GitHub (easiest)
3. **Create New Web Service:**
   - Click "New +" button
   - Select "Web Service"
   - Click "Connect a repository"
   - Find and select: `epiwatch-api`
4. **Configure Service:**
   ```
   Name: epiwatch-api
   Region: Choose closest to you
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. **Select Plan:**
   - Choose "Free" plan
6. **Click "Create Web Service"**

### Step 5: Wait for Deployment

- Render will build and deploy (takes 5-10 minutes)
- Watch the logs in real-time
- When done, you'll see: "Your service is live 🎉"

### Step 6: Get Your API URL

Your API will be available at:
```
https://epiwatch-api.onrender.com
```

Test it:
```
https://epiwatch-api.onrender.com/api/v1/health
```

---

## **Option B: Deploy via Docker (Alternative)**

If you prefer Docker deployment on Render:

### Step 1: Create Dockerfile

Already exists in your project! Located at: `docker/Dockerfile`

### Step 2: Push to GitHub (same as Option A, Steps 1-3)

### Step 3: Configure Render with Docker

In Render configuration:
```
Runtime: Docker
Dockerfile Path: docker/Dockerfile
Docker Command: (leave empty, uses CMD from Dockerfile)
```

---

## **Option C: Manual Deploy (No Git Required)**

If you don't want to use Git:

### Step 1: Create render.yaml

Already created! Located at: `epiwatch/render.yaml`

### Step 2: Create ZIP File

1. Compress your `epiwatch` folder
2. Name it: `epiwatch-api.zip`

### Step 3: Deploy via Render Dashboard

1. Go to: https://render.com
2. Sign up with email
3. Click "New +" → "Web Service"
4. Select "Deploy an existing image from a registry" 
   OR
5. Use "Blueprint" and upload your render.yaml

**Note:** This method is less convenient for updates.

---

## **Configuration Files Needed** ✅

### 1. render.yaml (Already Created!)
Located at: `epiwatch/render.yaml`

### 2. requirements.txt (Already Exists!)
Located at: `epiwatch/backend/requirements.txt`

### 3. Environment Variables (Optional)

If you need environment variables:
- In Render dashboard → Environment
- Add any API keys or secrets

---

## **After Deployment: Share with Your Friend** 🎉

Once deployed, your API will be at:
```
https://epiwatch-api.onrender.com
```

**Send your friend these endpoints:**

```kotlin
// Base URL for Android app
const val BASE_URL = "https://epiwatch-api.onrender.com"

// Example endpoints:
// Health check
GET https://epiwatch-api.onrender.com/api/v1/health

// Get alerts
GET https://epiwatch-api.onrender.com/api/v1/alerts?limit=20

// Get map data
GET https://epiwatch-api.onrender.com/api/v1/map

// Get trends
GET https://epiwatch-api.onrender.com/api/v1/trends

// Get statistics
GET https://epiwatch-api.onrender.com/api/v1/statistics

// Get diseases
GET https://epiwatch-api.onrender.com/api/v1/diseases
```

---

## **Important Notes** ⚠️

### Free Tier Limitations:
- **Spins down after 15 minutes of inactivity**
- First request after idle takes ~30 seconds to wake up
- 750 free hours per month
- Automatic HTTPS included

### Keep Service Active:
To prevent spin-down, you can:
1. Upgrade to paid plan ($7/month - always on)
2. Use a ping service (like UptimeRobot) to ping every 10 mins
3. Accept the 30-second wake-up delay

---

## **Troubleshooting** 🔧

### Issue: Build fails
**Solution:** Check that `requirements.txt` is in `backend/` folder

### Issue: Service starts but crashes
**Solution:** Check logs in Render dashboard for errors

### Issue: Can't find results folder
**Solution:** Make sure `results/` folder is committed to Git

### Issue: Import errors
**Solution:** Check that all imports use correct paths:
```python
from backend.country_coordinates import COUNTRY_COORDINATES
from backend.daily_simulator import DailyDataSimulator
```

---

## **Next Steps** 🎯

1. ✅ Install Git (if needed)
2. ✅ Create GitHub account
3. ✅ Push code to GitHub
4. ✅ Deploy on Render
5. ✅ Test your API
6. ✅ Share URL with your friend

---

## **Need Help?** 

I'm here to guide you through each step! Just let me know where you get stuck.

**Ready to start? Tell me:**
- Do you have Git installed? (check with: `git --version`)
- Do you have a GitHub account?
