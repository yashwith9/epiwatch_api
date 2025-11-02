# 🚀 spaCy NLP Integration for EpiWatch API

## ✅ Complete Setup Guide

### What We've Built:

A **lightweight spaCy-based disease classification system** integrated into your FastAPI backend.

---

## 📋 Step-by-Step Setup

### Step 1: Install spaCy

```powershell
cd "C:\Users\Bruger\OneDrive\Desktop\NLP\epi-watch\epiwatch"
pip install spacy==3.7.2
```

### Step 2: Train the spaCy Model

```powershell
python nlp/train_spacy_model.py
```

**What happens:**
- Loads your disease outbreak data from `results/disease_country_year_aggregates.csv`
- Trains a text classification model
- Creates input format: `"Country - WHO Region"`
- Predicts: Disease category
- Saves model to: `nlp/models/spacy_disease_classifier/`

**Expected Output:**
```
Training spaCy model with X disease categories...
Iteration 1/20 - Loss: X.XXXX
...
Model Accuracy: 0.XXXX
Model saved to: nlp/models/spacy_disease_classifier
```

### Step 3: Test the FastAPI Locally

```powershell
# Start the server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test the Prediction Endpoint

**Method 1: Using PowerShell**
```powershell
$body = @{
    country = "Kenya"
    who_region = "Africa"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/predict" -Method POST -Body $body -ContentType "application/json"
```

**Method 2: Using Python**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/predict",
    json={
        "country": "Kenya",
        "who_region": "Africa"
    }
)

print(response.json())
```

**Expected Response:**
```json
{
  "text": "Kenya - Africa",
  "predicted_disease": "Malaria",
  "confidence": 0.87,
  "top_predictions": [
    {"disease": "Malaria", "confidence": 0.87},
    {"disease": "Cholera", "confidence": 0.09},
    {"disease": "Yellow fever, unspecified", "confidence": 0.03},
    {"disease": "Dengue fever, unspecified", "confidence": 0.01},
    {"disease": "COVID-19", "confidence": 0.00}
  ]
}
```

---

## 🎯 API Endpoints

### New Prediction Endpoint

**POST `/api/v1/predict`**

Request body (Option 1 - Country + Region):
```json
{
  "country": "United States",
  "who_region": "Americas"
}
```

Request body (Option 2 - Direct Text):
```json
{
  "text": "Brazil - Americas"
}
```

Response:
```json
{
  "text": "Brazil - Americas",
  "predicted_disease": "Dengue fever, unspecified",
  "confidence": 0.92,
  "top_predictions": [
    {"disease": "Dengue fever, unspecified", "confidence": 0.92},
    {"disease": "Zika virus disease", "confidence": 0.05},
    {"disease": "Yellow fever, unspecified", "confidence": 0.02},
    ...
  ]
}
```

### All Existing Endpoints Still Work

- `GET /api/v1/health` - Health check
- `GET /api/v1/alerts` - Get alerts
- `GET /api/v1/map` - Map data
- `GET /api/v1/trends` - Trends
- `GET /api/v1/diseases` - Disease list
- `GET /api/v1/statistics` - Statistics
- `POST /api/v1/auth/signup` - Register
- `POST /api/v1/auth/login` - Login

---

## 📦 Files Created/Modified

### New Files:
1. **`nlp/train_spacy_model.py`** - Training script for spaCy model
2. **`backend/spacy_inference.py`** - Inference module for predictions
3. **`nlp/models/spacy_disease_classifier/`** - Trained model (after training)

### Modified Files:
1. **`backend/main.py`** - Added prediction endpoint
2. **`backend/requirements.txt`** - Added spacy==3.7.2

---

## 🚀 Deploy to Render

### Step 1: Commit & Push

```powershell
git add backend/main.py backend/requirements.txt backend/spacy_inference.py nlp/train_spacy_model.py
git commit -m "feat: add spaCy NLP disease prediction endpoint"
git push epiwatch_api main
```

### Step 2: Handle Model Files

**Option A: Include Model in Git (if small)**
```powershell
git add nlp/models/spacy_disease_classifier/
git commit -m "chore: add trained spaCy model"
git push epiwatch_api main
```

**Option B: Train on Render (add to build command in render.yaml)**
```yaml
buildCommand: pip install -r requirements.txt && python ../nlp/train_spacy_model.py
```

### Step 3: Update render.yaml (if needed)

```yaml
services:
  - type: web
    name: epiwatch-api
    runtime: python
    rootDirectory: backend
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    plan: starter
```

---

## 📱 Mobile App Integration

### Kotlin/Android Example:

```kotlin
data class PredictionRequest(
    val country: String,
    val who_region: String
)

data class PredictionResponse(
    val text: String,
    val predicted_disease: String,
    val confidence: Double,
    val top_predictions: List<TopPrediction>
)

data class TopPrediction(
    val disease: String,
    val confidence: Double
)

// Make prediction
suspend fun predictDisease(country: String, region: String): PredictionResponse {
    val request = PredictionRequest(country, region)
    
    return withContext(Dispatchers.IO) {
        val response = retrofit.create(ApiService::class.java)
            .predictDisease(request)
        response
    }
}
```

### Display in UI:

```kotlin
viewModelScope.launch {
    val prediction = predictDisease("Kenya", "Africa")
    
    // Show main prediction
    binding.diseaseName.text = prediction.predicted_disease
    binding.confidence.text = "${(prediction.confidence * 100).toInt()}%"
    
    // Show top predictions in RecyclerView
    adapter.submitList(prediction.top_predictions)
}
```

---

## 🎓 Model Performance

After training, check the model accuracy in the console output:

```
Model Accuracy: 0.XXXX (XXX/XXXX)
```

You can also test predictions:

```python
from backend.spacy_inference import get_classifier

classifier = get_classifier()

# Test various inputs
test_cases = [
    ("Kenya", "Africa"),
    ("United States", "Americas"),
    ("India", "South-East Asia"),
    ("Brazil", "Americas")
]

for country, region in test_cases:
    result = classifier.predict_country_region(country, region)
    print(f"{country}: {result['predicted_disease']} ({result['confidence']:.2%})")
```

---

## ✅ Advantages of spaCy vs Heavy Models

| Feature | spaCy | RoBERTa/BERT |
|---------|-------|--------------|
| **Size** | ~10-50MB | 400-500MB |
| **Training Time** | 1-5 minutes | 30-60 minutes |
| **Inference Speed** | <10ms | 100-200ms |
| **Deployment** | Easy | Complex (needs PyTorch) |
| **Memory** | Low (~100MB) | High (~2GB) |
| **Render Compatible** | ✅ Yes | ❌ Difficult |

---

## 🐛 Troubleshooting

### Model Not Found Error:

```
RuntimeError: spaCy model not found
```

**Solution:** Train the model first
```powershell
python nlp/train_spacy_model.py
```

### Import Error:

```
ModuleNotFoundError: No module named 'spacy'
```

**Solution:** Install spaCy
```powershell
pip install spacy==3.7.2
```

### Render Build Fails:

**Issue:** spaCy installation timeout

**Solution:** Add to render.yaml:
```yaml
buildCommand: pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
```

---

## 📊 Next Steps

1. ✅ Train the spaCy model locally
2. ✅ Test predictions locally
3. ✅ Commit and push to GitHub
4. ✅ Deploy to Render
5. ✅ Test production endpoint
6. ✅ Integrate with mobile app

---

**Your API URL (after deployment):**
```
https://your-service-name.onrender.com/api/v1/predict
```

**API Documentation:**
```
https://your-service-name.onrender.com/docs
```

---

## 🎉 Summary

You now have a complete disease prediction system with:
- ✅ Lightweight spaCy NLP model
- ✅ FastAPI prediction endpoint
- ✅ Easy Render deployment
- ✅ Mobile app ready API
- ✅ All existing endpoints working

The spaCy model will predict diseases based on country and WHO region, perfect for your mobile application!
