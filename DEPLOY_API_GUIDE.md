# Deploy EpiWatch API to Cloud

## 🚂 OPTION 1: Railway (Easiest, Free Tier)

### Step 1: Prepare Your Project

1. Create `requirements.txt` in backend folder:
```bash
cd C:\Users\Bruger\OneDrive\Desktop\NLP\epiwatch\backend
pip freeze > requirements.txt
```

2. Create `Procfile` in backend folder:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. Make sure your data files are included:
   - Copy `results/` folder to `backend/results/`

### Step 2: Deploy to Railway

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Connect your GitHub account
5. Push your code to GitHub first:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```
6. Select repository in Railway
7. Railway auto-detects Python and deploys!

**Your API will be at:** `https://your-app.up.railway.app`

**Free Tier:** $5 credit/month, no credit card required

---

## 🐳 OPTION 2: Docker + DigitalOcean

### Step 1: Create Dockerfile

Create `Dockerfile` in backend folder:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Build and test locally
```bash
docker build -t epiwatch-api .
docker run -p 8000:8000 epiwatch-api
```

### Step 3: Deploy to DigitalOcean

1. Create account at https://www.digitalocean.com/
2. Use App Platform (easiest)
3. Connect GitHub repo
4. DigitalOcean auto-builds from Dockerfile
5. Get public URL

**Cost:** $5-12/month

---

## ☁️ OPTION 3: Heroku (Simple)

### Step 1: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Prepare files

1. Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Create `runtime.txt`:
```
python-3.11.0
```

### Step 3: Deploy
```bash
cd backend
heroku login
heroku create epiwatch-api
git init
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

**Your API:** `https://epiwatch-api.herokuapp.com`

**Note:** Heroku removed free tier, now $5/month minimum

---

## 🌍 OPTION 4: Azure App Service

### Step 1: Install Azure CLI
```bash
# Download from https://aka.ms/installazurecliwindows
```

### Step 2: Deploy
```bash
az login
az webapp up --name epiwatch-api --runtime "PYTHON:3.11" --sku F1
```

**Free Tier:** Available (F1 SKU)

---

## ⚡ OPTION 5: Vercel (Serverless)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Create `vercel.json`
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### Step 3: Deploy
```bash
cd backend
vercel
```

**Free Tier:** Generous limits

---

## 🔒 OPTION 6: Cloudflare Tunnel (Free, Secure)

Like ngrok but free forever!

### Step 1: Install cloudflared
```bash
# Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

### Step 2: Authenticate
```bash
cloudflared tunnel login
```

### Step 3: Create tunnel
```bash
cloudflared tunnel create epiwatch-api
```

### Step 4: Configure tunnel

Create `config.yml`:
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: C:\Users\Bruger\.cloudflared\YOUR_TUNNEL_ID.json

ingress:
  - hostname: epiwatch-api.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

### Step 5: Run tunnel
```bash
cloudflared tunnel run epiwatch-api
```

**Free:** Forever, no limits!

---

## 📊 COMPARISON TABLE

| Option | Setup Time | Cost | Uptime | HTTPS | Best For |
|--------|-----------|------|--------|-------|----------|
| **ngrok** | 5 min | Free tier | While running | ✅ | Quick testing |
| **Local Network** | 2 min | Free | While PC on | ❌ | Same WiFi |
| **Railway** | 15 min | Free $5/mo | 24/7 | ✅ | Easy production |
| **DigitalOcean** | 30 min | $5-12/mo | 24/7 | ✅ | Full control |
| **Heroku** | 20 min | $5/mo | 24/7 | ✅ | Simple deploy |
| **Azure** | 25 min | Free tier | 24/7 | ✅ | Enterprise |
| **Vercel** | 10 min | Free | 24/7 | ✅ | Serverless |
| **Cloudflare** | 15 min | Free | While running | ✅ | Permanent free |

---

## 🎯 RECOMMENDATION

**For immediate sharing (today):**
→ Use **ngrok** (5 minutes, just works)

**For development (this week):**
→ Use **Railway** or **Vercel** (free, permanent URL)

**For production (launch):**
→ Use **DigitalOcean** or **Azure** (reliable, scalable)

---

## 🔐 SECURITY CONSIDERATIONS

When exposing your API:

1. **Add CORS properly** (already done in your main.py ✅)
2. **Add rate limiting:**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

3. **Add API key authentication:**
   ```python
   from fastapi.security import APIKeyHeader
   
   API_KEY = "your-secret-key"
   api_key_header = APIKeyHeader(name="X-API-Key")
   
   async def verify_api_key(api_key: str = Depends(api_key_header)):
       if api_key != API_KEY:
           raise HTTPException(status_code=403)
   ```

4. **Monitor usage** with logging

5. **Consider costs** - cloud services charge for bandwidth

---

## 📝 QUICK START: ngrok

Want to share RIGHT NOW? Here's the fastest way:

```powershell
# Terminal 1: Start your API
cd C:\Users\Bruger\OneDrive\Desktop\NLP\epiwatch\backend
python main.py

# Terminal 2: Start ngrok
ngrok http 8000

# Copy the https URL and send to your friend!
```

**Done in 5 minutes!** ⚡
