# EpiWatch - Disease Outbreak Detection System

**🚨 Production-grade AI system for early disease outbreak detection through real-time monitoring of online sources.**

![EpiWatch Architecture](docs/architecture.png)

## 🏗️ Architecture Overview

EpiWatch is a comprehensive modular system consisting of:

- **Data Ingestion**: Real-time collection from RSS feeds and news APIs
- **NLP Pipeline**: Disease and location extraction with confidence scoring
- **Anomaly Detection**: Prophet-based forecasting and outbreak alerts
- **Backend API**: FastAPI with PostgreSQL and Redis caching
- **Web Dashboard**: React frontend with interactive maps and charts
- **Mobile App**: Android application with push notifications

## 📁 Project Structure

```
epiwatch/
├── ingest/                 # Data ingestion services
├── nlp/                    # NLP: disease & location extraction  
├── models/                 # Forecasting & anomaly detection
├── etl/                    # Data aggregation pipeline
├── backend/                # FastAPI backend + API routes
├── frontend/               # React web dashboard
├── mobile/                 # Android app (Kotlin)
├── data/                   # Dictionaries, cleaned datasets
├── tests/                  # Unit & integration tests
├── docker/                 # Dockerfiles
└── .github/workflows/      # CI/CD pipelines
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+
- Android Studio (for mobile development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd epiwatch
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python backend/db/init_db.py

# Start services
docker-compose up -d
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 4. Mobile App Setup
```bash
cd mobile
./gradlew assembleDebug
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/epiwatch
REDIS_URL=redis://localhost:6379

# API Keys
NEWS_API_KEY=your_news_api_key
GDELT_API_KEY=your_gdelt_key

# Authentication
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256

# Mobile
FIREBASE_SERVER_KEY=your_firebase_key

# External Services
MAPBOX_ACCESS_TOKEN=your_mapbox_token
```

## 🔄 Data Pipeline

1. **Ingestion**: Collects data from RSS feeds, news APIs (GDELT, NewsAPI)
2. **NLP Processing**: Extracts diseases and locations using spaCy and fuzzy matching
3. **ETL Aggregation**: Builds daily/weekly aggregates per (disease, country)
4. **Anomaly Detection**: Uses Prophet for forecasting and detects outbreaks
5. **API Serving**: Provides real-time data through REST endpoints
6. **Alerting**: Sends push notifications for high-severity alerts

## 📱 Features

### Web Dashboard
- 🗺️ Interactive world map with outbreak hotspots
- 📈 Trend analysis and forecasting charts
- 🚨 Real-time alerts feed with severity filtering
- 🔍 Disease and location-based search
- 📊 Historical outbreak data visualization

### Mobile App
- 📱 Push notifications for new outbreaks
- 🗺️ Native map integration with markers
- 📋 Alerts list with filtering capabilities
- 📈 Trend charts for selected diseases/locations
- ⚙️ Customizable notification preferences
- 🌙 Dark/light theme support

### API Endpoints
- `GET /alerts` - Active alerts with severity filtering
- `GET /map` - Geospatial outbreak data for mapping
- `GET /trends` - Historical and forecasted trends
- `POST /feedback` - User feedback collection
- `GET /diseases` - Supported disease dictionary
- `GET /health` - System health monitoring

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_nlp.py
python -m pytest tests/test_models.py

# Run with coverage
python -m pytest tests/ --cov=epiwatch --cov-report=html
```

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Scale ingestion workers
docker-compose up --scale ingest-worker=3

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring & Alerts

- **System Health**: `/health` endpoint with service status
- **Performance Metrics**: Redis-cached response times
- **Data Quality**: NLP confidence score monitoring
- **Alert Thresholds**: Configurable severity levels
- **Logging**: Structured JSON logs with ELK stack integration

## 🔐 Security

- JWT-based authentication for API access
- CORS configuration for web/mobile clients
- Rate limiting on all endpoints
- Input validation and sanitization
- Secure environment variable handling
- SSL/TLS encryption in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Submit a Pull Request

## 📋 Development Roadmap

- [ ] **Phase 1**: Core data pipeline and NLP
- [ ] **Phase 2**: Anomaly detection and alerting
- [ ] **Phase 3**: Web dashboard and API
- [ ] **Phase 4**: Mobile application
- [ ] **Phase 5**: Advanced ML models and forecasting
- [ ] **Phase 6**: Multi-language support
- [ ] **Phase 7**: Social media integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@epiwatch.ai
- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/epiwatch/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/epiwatch/discussions)

## 🙏 Acknowledgments

- World Health Organization (WHO) for disease classification standards
- GDELT Project for global news monitoring
- spaCy team for NLP framework
- Prophet team for time series forecasting
- OpenStreetMap contributors for geospatial data

---

**⚡ Built with passion for global health monitoring and early outbreak detection.**