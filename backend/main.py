"""
EpiWatch - FastAPI Backend Server
===================================

REST API endpoints for disease outbreak monitoring system.

Endpoints:
    GET  /api/v1/health          - Health check
    GET  /api/v1/alerts           - Get recent alerts
    GET  /api/v1/alerts/{id}      - Get specific alert
    GET  /api/v1/map              - Get outbreak map data
    GET  /api/v1/trends           - Get 7-day disease trends
    GET  /api/v1/diseases         - List all diseases
    GET  /api/v1/statistics       - Get dashboard statistics
    POST /api/v1/feedback         - Submit user feedback
    POST /api/v1/auth/signup      - User registration
    POST /api/v1/auth/login       - User authentication
    GET  /api/v1/auth/validate    - Token validation

Run:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
from pathlib import Path
import json
import uvicorn

# Import our enhanced modules
try:
    from epiwatch.backend.country_coordinates import COUNTRY_COORDINATES
    from epiwatch.backend.daily_simulator import DailyDataSimulator
except ImportError:
    try:
        from backend.country_coordinates import COUNTRY_COORDINATES
        from backend.daily_simulator import DailyDataSimulator
    except ImportError:
        from country_coordinates import COUNTRY_COORDINATES
        from daily_simulator import DailyDataSimulator

# Import spaCy inference
try:
    from backend.spacy_inference import get_classifier
except ImportError:
    from spacy_inference import get_classifier


# ============================================================================
# Data Models
# ============================================================================

class SeverityLevel(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(str, Enum):
    """Geographic risk levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Alert(BaseModel):
    """Disease outbreak alert"""
    id: str
    timestamp: str
    disease: str
    location: str
    city_location: Optional[str] = None  # Enhanced: city-level location
    context_description: Optional[str] = None  # Enhanced: contextual outbreak description
    date: str
    actual_count: int
    expected_count: float
    deviation: float
    deviation_pct: float
    severity: float
    severity_level: SeverityLevel
    anomaly_type: str
    z_score: float
    message: str


class MapOutbreak(BaseModel):
    """Outbreak location for map display"""
    id: str
    disease: str
    country: str
    iso3: str
    latitude: float
    longitude: float
    outbreak_count: int
    risk_level: RiskLevel
    year: int


class TrendPoint(BaseModel):
    """Single data point in 7-day trend"""
    date: str
    count: int


class DiseaseTrend(BaseModel):
    """7-day trend for a disease"""
    disease: str
    total_count: int
    trend_data: List[TrendPoint]
    change_pct: float
    trend_direction: str  # "up", "down", "stable"
    severity: Optional[str] = None  # Enhanced: severity level from daily simulator
    description: Optional[str] = None  # Enhanced: contextual description
    severity: Optional[str] = None  # Enhanced: severity level from daily simulator
    description: Optional[str] = None  # Enhanced: contextual description


class DiseaseStatistic(BaseModel):
    """Disease statistics for dashboard"""
    disease: str
    current_count: int
    change_pct: float
    trend: str  # "up" or "down"


class DashboardStats(BaseModel):
    """Main dashboard statistics"""
    total_outbreaks: int
    active_diseases: int
    affected_countries: int
    last_updated: str
    top_diseases: List[DiseaseStatistic]  # Changed from disease_stats to match API response


class FeedbackRequest(BaseModel):
    """User feedback submission"""
    alert_id: Optional[str] = None
    feedback_type: str = Field(..., description="Type: 'false_positive', 'confirmed', 'additional_info'")
    comment: Optional[str] = None
    user_email: Optional[str] = None


class DiseasePredictionRequest(BaseModel):
    """Request for disease prediction"""
    country: Optional[str] = Field(None, description="Country name")
    who_region: Optional[str] = Field(None, description="WHO region")
    text: Optional[str] = Field(None, description="Direct text input (Country - WHO region)")


class TopPrediction(BaseModel):
    """Single prediction result"""
    disease: str
    confidence: float


class DiseasePredictionResponse(BaseModel):
    """Response from disease prediction"""
    text: str
    predicted_disease: str
    confidence: float
    top_predictions: List[TopPrediction]


# ============================================================================
# Data Service Layer
# ============================================================================

class DataService:
    """Service for loading and processing outbreak data"""
    
    def __init__(self, data_dir: str = "results"):
        self.data_dir = Path(data_dir)
        self.anomaly_dir = self.data_dir / "anomaly_detection"
        self.daily_simulator = DailyDataSimulator()  # Initialize daily data simulator
        self._load_data()
    
    def _load_data(self):
        """Load all required data files"""
        # Load aggregated data
        self.disease_country_year = pd.read_csv(
            self.data_dir / "disease_country_year_aggregates.csv"
        )
        self.disease_year = pd.read_csv(
            self.data_dir / "disease_year_global_aggregates.csv"
        )
        self.country_year = pd.read_csv(
            self.data_dir / "country_year_aggregates.csv"
        )
        
        # Load alerts from anomaly detection
        self.alerts = self._load_all_alerts()
        
        # Use complete country coordinates database (233 countries!)
        self.country_coords = COUNTRY_COORDINATES
    
    def _load_all_alerts(self) -> List[Dict]:
        """Load all alerts from anomaly detection results"""
        all_alerts = []
        
        if not self.anomaly_dir.exists():
            return all_alerts
        
        # Load all alert JSON files
        for alert_file in self.anomaly_dir.glob("*_alerts.json"):
            try:
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
                    # Add unique ID and enhance each alert
                    for idx, alert in enumerate(alerts):
                        alert['id'] = f"{alert_file.stem}_{idx}"
                        # Enhance alert with city location and context
                        self._enhance_alert(alert)
                    all_alerts.extend(alerts)
            except Exception as e:
                print(f"Error loading {alert_file}: {e}")
        
        # Sort by severity (highest first)
        all_alerts.sort(key=lambda x: x['severity'], reverse=True)
        
        return all_alerts
    
    def _enhance_alert(self, alert: Dict) -> None:
        """Enhance alert with city-level location and contextual description"""
        disease = alert.get('disease', '')
        country = alert.get('country', 'Global')
        severity = alert.get('severity', 0)
        
        # Generate city-level location based on country
        alert['city_location'] = self._generate_city_location(country, disease)
        
        # Generate contextual description based on disease and severity
        alert['context_description'] = self._generate_alert_context(disease, severity, country)
    
    def _generate_city_location(self, country: str, disease: str) -> str:
        """Generate realistic city-level location for outbreak"""
        # Major cities by country for realistic simulation
        city_map = {
            'United States': ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ'],
            'China': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu'],
            'India': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai'],
            'Brazil': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza'],
            'Nigeria': ['Lagos', 'Kano', 'Ibadan', 'Abuja', 'Port Harcourt'],
            'Democratic Republic of the Congo': ['Kinshasa', 'Lubumbashi', 'Mbuji-Mayi', 'Kananga', 'Kisangani'],
            'Saudi Arabia': ['Riyadh', 'Jeddah', 'Mecca', 'Medina', 'Dammam'],
            'France': ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice'],
            'United Kingdom': ['London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow'],
            'Kenya': ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret'],
        }
        
        if country in city_map:
            import random
            return random.choice(city_map[country])
        else:
            # Return country name if no city mapping
            return country
    
    def _generate_alert_context(self, disease: str, severity: float, country: str) -> str:
        """Generate contextual description for alert"""
        import random
        
        # Context templates based on severity
        if severity >= 80:
            contexts = [
                f"Rapid spread in downtown area schools and residential neighborhoods",
                f"Critical outbreak detected in metro region with accelerating transmission",
                f"Emergency response activated in urban centers",
                f"Widespread community transmission across multiple districts"
            ]
        elif severity >= 60:
            contexts = [
                f"Elevated transmission rates in community settings",
                f"Outbreak expanding beyond initial containment area",
                f"Multiple clusters identified in urban and suburban areas",
                f"Increased cases reported in healthcare facilities"
            ]
        elif severity >= 40:
            contexts = [
                f"Localized outbreak in residential area",
                f"Cluster detected in community center",
                f"Cases emerging in school district",
                f"Contained spread in specific neighborhoods"
            ]
        else:
            contexts = [
                f"Isolated cases under investigation",
                f"Small cluster identified and monitored",
                f"Limited transmission in controlled area",
                f"Sporadic cases with no clear pattern"
            ]
        
        # Disease-specific context additions
        disease_contexts = {
            'Influenza': " - seasonal peak activity",
            'Dengue': " - vector-borne transmission surge",
            'Measles': " - vaccination gap identified",
            'Polio': " - immunization campaign underway",
            'Cholera': " - water supply contamination suspected",
            'Malaria': " - mosquito control measures deployed",
            'Tuberculosis': " - contact tracing initiated",
            'COVID-19': " - variant surveillance active",
            'Ebola': " - quarantine protocols enforced",
            'Yellow Fever': " - vector control intensified"
        }
        
        base_context = random.choice(contexts)
        disease_suffix = disease_contexts.get(disease, "")
        
        return base_context + disease_suffix
    
    def get_recent_alerts(
        self,
        limit: int = 20,
        severity: Optional[str] = None,
        disease: Optional[str] = None
    ) -> List[Dict]:
        """Get recent alerts with optional filtering"""
        filtered = self.alerts.copy()
        
        # Filter by severity
        if severity:
            filtered = [a for a in filtered if a['severity_level'] == severity]
        
        # Filter by disease
        if disease:
            filtered = [a for a in filtered if a['disease'].lower() == disease.lower()]
        
        return filtered[:limit]
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict]:
        """Get specific alert by ID"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                return alert
        return None
    
    def get_map_data(
        self,
        year: Optional[int] = None,
        disease: Optional[str] = None
    ) -> List[Dict]:
        """Get outbreak data for map visualization"""
        df = self.disease_country_year.copy()
        
        # Filter by year (default to latest)
        if year is None:
            year = df['Year'].max()
        df = df[df['Year'] == year]
        
        # Filter by disease
        if disease:
            df = df[df['Disease'] == disease]
        
        # Calculate risk levels
        df['risk_level'] = df['outbreak_count'].apply(self._calculate_risk_level)
        
        # Add coordinates
        map_data = []
        for _, row in df.iterrows():
            iso3 = row['iso3']
            if iso3 in self.country_coords:
                coords = self.country_coords[iso3]
                map_data.append({
                    'id': f"{row['Disease']}_{iso3}_{year}",
                    'disease': row['Disease'],
                    'country': row['Country'],
                    'iso3': iso3,
                    'latitude': coords['lat'],
                    'longitude': coords['lon'],
                    'outbreak_count': int(row['outbreak_count']),
                    'risk_level': row['risk_level'],
                    'year': year
                })
        
        return map_data
    
    def _calculate_risk_level(self, count: int) -> str:
        """Calculate risk level from outbreak count"""
        if count >= 10:
            return "high"
        elif count >= 5:
            return "medium"
        else:
            return "low"
    
    def get_7day_trends(self, diseases: Optional[List[str]] = None) -> List[Dict]:
        """
        Get 7-day trends for diseases
        Note: This uses yearly data, simulating 7-day trends from annual patterns
        """
        df = self.disease_year.copy()
        
        # Get top diseases if not specified
        if diseases is None:
            top_diseases = df.groupby('Disease')['outbreak_count'].sum().nlargest(4).index
            diseases = list(top_diseases)
        
        trends = []
        for disease in diseases:
            disease_data = df[df['Disease'] == disease].sort_values('Year')
            
            if len(disease_data) < 1:
                continue
            
            # Use daily simulator for realistic 7-day trend with seasonal patterns
            latest_year = disease_data['Year'].max()
            latest_count = disease_data[disease_data['Year'] == latest_year]['outbreak_count'].values[0]
            
            # Generate realistic daily breakdown for past 7 days
            daily_data = self.daily_simulator.generate_daily_breakdown(
                yearly_count=latest_count,
                year=latest_year,
                disease=disease,
                days_back=7
            )
            
            # Format trend data for API response
            trend_data = [
                {
                    'date': item['date'],
                    'count': item['count']
                }
                for item in daily_data
            ]
            
            # Calculate realistic change using simulator
            current_week_total = sum(item['count'] for item in daily_data)
            
            # Get previous week comparison (simulate previous 7 days)
            prev_daily_data = self.daily_simulator.generate_daily_breakdown(
                yearly_count=latest_count,
                year=latest_year,
                disease=disease,
                days_back=14  # Get 14 days to compare week 2 vs week 1
            )
            prev_week_total = sum(item['count'] for item in prev_daily_data[:7])
            
            change_stats = self.daily_simulator.calculate_realistic_change(
                current_count=current_week_total,
                previous_count=prev_week_total,
                time_period='week'
            )
            
            trends.append({
                'disease': disease,
                'total_count': current_week_total,
                'trend_data': trend_data,
                'change_pct': change_stats['change_pct'],
                'trend_direction': change_stats['trend'],
                'severity': change_stats['severity'],
                'description': change_stats['description']
            })
        
        return trends
    
    def get_dashboard_statistics(self) -> Dict:
        """Get main dashboard statistics"""
        # Calculate totals
        latest_year = self.disease_country_year['Year'].max()
        current_data = self.disease_country_year[
            self.disease_country_year['Year'] == latest_year
        ]
        
        total_outbreaks = current_data['outbreak_count'].sum()
        active_diseases = current_data['Disease'].nunique()
        affected_countries = current_data['Country'].nunique()
        
        # Get top 4 diseases with stats
        disease_stats = []
        top_diseases = current_data.groupby('Disease')['outbreak_count'].sum().nlargest(4)
        
        for disease, count in top_diseases.items():
            # Calculate change from previous year
            prev_year_data = self.disease_year[
                (self.disease_year['Disease'] == disease) &
                (self.disease_year['Year'] == latest_year - 1)
            ]
            
            if len(prev_year_data) > 0:
                prev_count = prev_year_data['outbreak_count'].values[0]
                change_pct = ((count - prev_count) / (prev_count + 1)) * 100
            else:
                change_pct = 0
            
            disease_stats.append({
                'disease': disease,
                'current_count': int(count),
                'change_pct': round(change_pct, 1),
                'trend': 'up' if change_pct > 0 else 'down'
            })
        
        return {
            'total_outbreaks': int(total_outbreaks),
            'active_diseases': active_diseases,
            'affected_countries': affected_countries,
            'last_updated': datetime.now().isoformat(),
            'top_diseases': disease_stats  # Changed from disease_stats to top_diseases
        }
    
    def get_all_diseases(self) -> List[str]:
        """Get list of all diseases"""
        return sorted(self.disease_year['Disease'].unique().tolist())


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="EpiWatch API",
    description="Disease Outbreak Detection and Monitoring System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "*"],  # Add mobile app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
try:
    from backend.database import init_db
    from backend.auth_routes import router as auth_router
except ImportError:
    from database import init_db
    from auth_routes import router as auth_router

init_db()

# Include authentication routes
app.include_router(auth_router)

# Initialize data service
# Use absolute path to results directory
import os
results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
data_service = DataService(data_dir=results_dir)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "EpiWatch API",
        "version": "1.0.0"
    }


@app.get("/api/v1/alerts", response_model=List[Alert])
async def get_alerts(
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[SeverityLevel] = None,
    disease: Optional[str] = None
):
    """
    Get recent outbreak alerts
    
    - **limit**: Number of alerts to return (1-100)
    - **severity**: Filter by severity level
    - **disease**: Filter by disease name
    """
    alerts = data_service.get_recent_alerts(
        limit=limit,
        severity=severity.value if severity else None,
        disease=disease
    )
    return alerts


@app.get("/api/v1/alerts/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """Get specific alert by ID"""
    alert = data_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@app.get("/api/v1/map", response_model=List[MapOutbreak])
async def get_map_data(
    year: Optional[int] = None,
    disease: Optional[str] = None
):
    """
    Get outbreak data for map visualization
    
    - **year**: Year to display (default: latest)
    - **disease**: Filter by specific disease
    """
    map_data = data_service.get_map_data(year=year, disease=disease)
    return map_data


@app.get("/api/v1/trends", response_model=List[DiseaseTrend])
async def get_trends(
    diseases: Optional[str] = Query(None, description="Comma-separated disease names")
):
    """
    Get 7-day disease trends
    
    - **diseases**: Comma-separated list of diseases (default: top 4)
    """
    disease_list = diseases.split(',') if diseases else None
    trends = data_service.get_7day_trends(diseases=disease_list)
    return trends


@app.get("/api/v1/diseases")
async def get_diseases():
    """Get list of all diseases in the system"""
    diseases = data_service.get_all_diseases()
    return {"diseases": diseases, "count": len(diseases)}


@app.get("/api/v1/statistics", response_model=DashboardStats)
async def get_statistics():
    """Get dashboard statistics"""
    stats = data_service.get_dashboard_statistics()
    return stats


@app.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback on alerts
    
    - **alert_id**: Alert being reviewed (optional)
    - **feedback_type**: Type of feedback
    - **comment**: Additional comments
    """
    # In production, save to database
    return {
        "status": "success",
        "message": "Feedback received",
        "feedback_id": f"fb_{datetime.now().timestamp()}"
    }


@app.post("/api/v1/predict", response_model=DiseasePredictionResponse)
async def predict_disease(request: DiseasePredictionRequest):
    """
    Predict disease outbreak based on country and WHO region using spaCy NLP model
    
    - **text**: Direct text input (e.g., "Kenya - Africa")
    - **country**: Country name (alternative to text)
    - **who_region**: WHO region (alternative to text)
    
    Returns predicted disease with confidence scores
    """
    try:
        classifier = get_classifier()
        
        # Use direct text if provided, otherwise build from country/region
        if request.text:
            result = classifier.predict(request.text, top_k=5)
        elif request.country and request.who_region:
            result = classifier.predict_country_region(
                request.country, 
                request.who_region, 
                top_k=5
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'text' or both 'country' and 'who_region' must be provided"
            )
        
        return result
        
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "EpiWatch API",
        "version": "1.0.0",
        "description": "Disease Outbreak Detection and Monitoring System with spaCy NLP",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "alerts": "/api/v1/alerts",
            "map": "/api/v1/map",
            "trends": "/api/v1/trends",
            "diseases": "/api/v1/diseases",
            "statistics": "/api/v1/statistics",
            "predict": "/api/v1/predict"
        }
    }

    return {
        "status": "success",
        "message": "Feedback received successfully",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "EpiWatch API",
        "version": "1.0.0",
        "description": "Disease Outbreak Detection and Monitoring System",
        "docs": "/api/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "alerts": "/api/v1/alerts",
            "map": "/api/v1/map",
            "trends": "/api/v1/trends",
            "diseases": "/api/v1/diseases",
            "statistics": "/api/v1/statistics"
        }
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
