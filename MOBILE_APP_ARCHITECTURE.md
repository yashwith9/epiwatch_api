# EpiWatch Mobile App Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EPIWATCH MOBILE APPLICATION                         │
│                         (Android - Kotlin + Jetpack Compose)                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              📱 UI LAYER (Compose)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ Dashboard Screen │  │  Trends Screen   │  │  Alerts Screen   │          │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤          │
│  │ • Stats Cards    │  │ • 7-Day Charts   │  │ • Alert Cards    │          │
│  │ • Google Map     │  │ • Trend Badges   │  │ • City Locations │          │
│  │ • Disease Cards  │  │ • Change %       │  │ • Context Desc.  │          │
│  │ • Action Buttons │  │ • Severity Tags  │  │ • Severity Filter│          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│          ↑                     ↑                     ↑                      │
│          └─────────────────────┴─────────────────────┘                      │
│                                 │                                           │
│                    ┌────────────┴────────────┐                              │
│                    │   Navigation Graph      │                              │
│                    │  (NavController)        │                              │
│                    └─────────────────────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↕ (StateFlow)

┌─────────────────────────────────────────────────────────────────────────────┐
│                        🧠 VIEWMODEL LAYER (State Management)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │ DashboardViewModel   │  │  TrendsViewModel     │  │  AlertsViewModel │  │
│  ├──────────────────────┤  ├──────────────────────┤  ├──────────────────┤  │
│  │ • UiState Flow       │  │ • UiState Flow       │  │ • UiState Flow   │  │
│  │ • Load Statistics    │  │ • Load Trends        │  │ • Load Alerts    │  │
│  │ • Load Map Data      │  │ • Filter Diseases    │  │ • Filter Severity│  │
│  │ • Error Handling     │  │ • Error Handling     │  │ • Error Handling │  │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↕ (suspend functions)

┌─────────────────────────────────────────────────────────────────────────────┐
│                        💾 REPOSITORY LAYER (Business Logic)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌─────────────────────────────────┐                      │
│                    │   EpiWatchRepository            │                      │
│                    ├─────────────────────────────────┤                      │
│                    │ • getHealth()                   │                      │
│                    │ • getStatistics()               │                      │
│                    │ • getMapData()                  │                      │
│                    │ • getTrends()                   │                      │
│                    │ • getAlerts()                   │                      │
│                    │ • getDiseases()                 │                      │
│                    │                                 │                      │
│                    │ Error Handling + Coroutines     │                      │
│                    └─────────────────────────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↕ (Retrofit HTTP calls)

┌─────────────────────────────────────────────────────────────────────────────┐
│                        🌐 NETWORK LAYER (Retrofit + OkHttp)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  EpiWatchApiService (Retrofit Interface)                             │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  GET /api/v1/health          → HealthCheck                           │  │
│  │  GET /api/v1/statistics      → DashboardStats                        │  │
│  │  GET /api/v1/map             → List<MapOutbreak>                     │  │
│  │  GET /api/v1/trends          → List<DiseaseTrend>                    │  │
│  │  GET /api/v1/alerts          → List<Alert>                           │  │
│  │  GET /api/v1/diseases        → List<String>                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  RetrofitClient                                                       │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  • OkHttpClient (with logging)                                       │  │
│  │  • GsonConverterFactory (JSON parsing)                               │  │
│  │  • Base URL: http://10.0.2.2:8000/ (emulator)                        │  │
│  │              http://YOUR_IP:8000/ (real device)                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↕ (HTTP/JSON)

┌─────────────────────────────────────────────────────────────────────────────┐
│                        🖥️  EPIWATCH API SERVER (FastAPI)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Running on: http://localhost:8000                                         │
│  Location: C:\Users\Bruger\OneDrive\Desktop\NLP\epiwatch\backend           │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  7 REST Endpoints (all tested ✅)                                     │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  /api/v1/health      - Health check                                  │  │
│  │  /api/v1/statistics  - Dashboard stats + top diseases                │  │
│  │  /api/v1/map         - 207 locations, 143 countries                  │  │
│  │  /api/v1/trends      - 7-day daily data with seasonal patterns       │  │
│  │  /api/v1/alerts      - Alerts with city locations + context          │  │
│  │  /api/v1/diseases    - List of all diseases                          │  │
│  │  /api/v1/feedback    - Submit user feedback                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Enhanced Features:                                                        │
│  ✅ 233 country coordinates database                                       │
│  ✅ Realistic daily data simulation (seasonal patterns)                    │
│  ✅ City-level locations (50+ cities mapped)                               │
│  ✅ Contextual alert descriptions                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↕

┌─────────────────────────────────────────────────────────────────────────────┐
│                        📊 DATA LAYER (CSV + JSON)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Location: C:\Users\Bruger\OneDrive\Desktop\NLP\epiwatch\results           │
│                                                                             │
│  • disease_country_year_aggregates.csv      (2,357 records)                │
│  • disease_year_global_aggregates.csv                                      │
│  • country_year_aggregates.csv                                             │
│  • anomaly_detection/*.json                 (2 critical alerts)            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 DATA FLOW EXAMPLE

### User Opens Dashboard Screen:

```
1. User → Tap App Icon
              ↓
2. MainActivity → Initialize EpiWatchNavGraph
              ↓
3. DashboardScreen (Composable) → Rendered
              ↓
4. DashboardViewModel → Created (init block runs)
              ↓
5. viewModelScope.launch → Coroutine started
              ↓
6. repository.getStatistics() → Suspend function called
              ↓
7. RetrofitClient.apiService.getStatistics() → HTTP GET request
              ↓
8. Network: GET http://10.0.2.2:8000/api/v1/statistics
              ↓
9. FastAPI Server → Processes request
              ↓
10. DataService.get_dashboard_statistics() → Reads CSV files
              ↓
11. Response: JSON { total_outbreaks: 207, active_diseases: 21, ... }
              ↓
12. Retrofit → Parses JSON to DashboardStats object
              ↓
13. Repository → Returns Result.success(DashboardStats)
              ↓
14. ViewModel → Updates _uiState.value
              ↓
15. StateFlow → Emits new state
              ↓
16. DashboardScreen → Recomposes with new data
              ↓
17. User → Sees stats cards, map, disease cards! 🎉
```

---

## 🛠️ TECHNOLOGY STACK SUMMARY

### Mobile App (Android)
- **Language:** Kotlin
- **UI Framework:** Jetpack Compose (Material Design 3)
- **Navigation:** Navigation Compose
- **Networking:** Retrofit + OkHttp
- **Async:** Coroutines + Flow
- **State Management:** ViewModel + StateFlow
- **Dependency Injection:** Manual (simple app)
- **Maps:** Google Maps Compose
- **Charts:** Vico Charts
- **JSON Parsing:** Gson
- **Image Loading:** Coil

### Backend API (Python)
- **Framework:** FastAPI
- **Server:** Uvicorn (ASGI)
- **Data:** Pandas, NumPy
- **AI/ML:** Prophet (forecasting), spaCy (NLP)
- **Database:** PostgreSQL (configured, not yet used)
- **Cache:** Redis (configured, not yet used)

### Data Pipeline
- **Source:** disease_outbreaks_minimal.csv (2,357 records)
- **Processing:** ETL scripts, aggregation
- **Anomaly Detection:** Prophet time series forecasting
- **Storage:** CSV files + JSON

---

## 📦 PROJECT STRUCTURE

```
C:\Users\Bruger\OneDrive\Desktop\NLP\
└── epiwatch/
    ├── backend/                         # FastAPI server ✅
    │   ├── main.py                      # 7 REST endpoints
    │   ├── country_coordinates.py       # 233 countries
    │   └── daily_simulator.py           # Seasonal patterns
    ├── frontend/
    │   └── dashboard.html               # Web dashboard ✅
    ├── models/
    │   └── anomaly_detector.py          # Prophet ML ✅
    ├── nlp/
    │   ├── disease_extractor.py         # 150+ diseases ✅
    │   └── location_extractor.py        # City/country NLP ✅
    ├── results/
    │   ├── *.csv                        # Aggregated data ✅
    │   └── anomaly_detection/*.json     # Alerts ✅
    ├── MOBILE_APP_GUIDE.md              # Setup guide ✅
    ├── MOBILE_APP_SCREENS.md            # UI code ✅
    ├── MOBILE_APP_CHECKLIST.md          # Quick start ✅
    └── MOBILE_APP_ARCHITECTURE.md       # This file ✅
```

---

## 🎯 DEVELOPMENT TIMELINE

### Phase 1: Backend (COMPLETE ✅)
- Data ingestion service
- NLP pipeline
- ETL & aggregation
- Anomaly detection
- FastAPI with 7 endpoints
- 4 major enhancements

### Phase 2: Mobile App (YOU ARE HERE 👇)
- Project setup
- Data models & API integration
- 3 screens (Dashboard, Trends, Alerts)
- Navigation
- Google Maps integration

### Phase 3: Advanced Features (FUTURE)
- Push notifications (Firebase)
- Offline support (Room DB)
- User authentication
- Data export
- Dark mode
- Unit & UI tests

### Phase 4: Deployment (FUTURE)
- Docker containerization
- CI/CD pipeline
- Google Play Store
- Production monitoring

---

**Your Next Step:** Start with `MOBILE_APP_CHECKLIST.md` Step 1! 🚀
