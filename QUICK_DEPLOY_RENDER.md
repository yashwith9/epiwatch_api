# Quick Deploy to Render - Commands Cheat Sheet

## 🚀 FASTEST PATH: Deploy to Render

### Step 1: Install Git (First Time Only)
1. Download: https://git-scm.com/download/win
2. Install with default settings
3. Close and reopen PowerShell

### Step 2: Quick Commands (Copy & Paste)

```powershell
# Navigate to project
cd C:\Users\Bruger\OneDrive\Desktop\NLP\epi-watch\epiwatch

# Check if git is installed
git --version

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Deploy EpiWatch API to Render"

# STOP HERE - Now go to GitHub
```

### Step 3: Create GitHub Repository
1. Go to: https://github.com/new
2. Name: `epiwatch-api`
3. Public repository
4. Click "Create repository"
5. **Copy the commands GitHub shows you** (similar to below)

### Step 4: Push to GitHub

```powershell
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/epiwatch-api.git
git branch -M main
git push -u origin main
```

**If asked for credentials:**
- Username: Your GitHub username
- Password: Create token at https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Select: `repo` checkbox
  - Copy the token and use it as password

### Step 5: Deploy on Render
1. Go to: https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest!)
4. Click "New +" → "Web Service"
5. Connect your `epiwatch-api` repository
6. Use these settings:
   ```
   Name: epiwatch-api
   Branch: main
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```
7. Click "Create Web Service"

### Step 6: Wait & Test (5-10 minutes)
- Watch the deployment logs
- When done, you'll get URL like: `https://epiwatch-api.onrender.com`

### Step 7: Test Your API

Open browser and visit:
```
https://epiwatch-api.onrender.com/api/v1/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "EpiWatch API",
  "version": "1.0.0"
}
```

### Step 8: Share with Your Friend 🎉

Send him this:
```
Base URL: https://epiwatch-api.onrender.com

Endpoints:
- /api/v1/health
- /api/v1/alerts
- /api/v1/map
- /api/v1/trends
- /api/v1/statistics
- /api/v1/diseases
```

---

## ⚠️ Common Issues & Solutions

### "git is not recognized"
**Solution:** Install Git from https://git-scm.com/download/win and restart terminal

### "Permission denied" when pushing
**Solution:** Use Personal Access Token instead of password
- Generate at: https://github.com/settings/tokens

### Build fails on Render
**Solution:** Check that:
1. `backend/requirements.txt` exists
2. `backend/main.py` exists
3. `results/` folder is committed

### "results folder not found"
**Solution:** Make sure results folder is in Git:
```powershell
git add results/
git commit -m "Add results folder"
git push
```

---

## 📱 For Your Friend (Android Developer)

Share this code snippet:

```kotlin
// In your API service file
object ApiConfig {
    const val BASE_URL = "https://epiwatch-api.onrender.com"
    
    // Add trailing slash if needed
    const val API_BASE_URL = "$BASE_URL/api/v1/"
}

// Example usage with Retrofit
interface EpiWatchApi {
    @GET("health")
    suspend fun getHealth(): Response<HealthResponse>
    
    @GET("alerts")
    suspend fun getAlerts(
        @Query("limit") limit: Int = 20
    ): Response<List<Alert>>
    
    @GET("map")
    suspend fun getMapData(
        @Query("disease") disease: String? = null
    ): Response<List<MapOutbreak>>
    
    @GET("trends")
    suspend fun getTrends(): Response<List<DiseaseTrend>>
    
    @GET("statistics")
    suspend fun getStatistics(): Response<DashboardStats>
}
```

---

## 🎯 Summary

1. ✅ Install Git
2. ✅ Push code to GitHub
3. ✅ Deploy on Render
4. ✅ Get public URL
5. ✅ Share with friend

**Time needed:** 15-20 minutes (first time)

---

Ready? Start with Step 1! Let me know if you get stuck anywhere.
