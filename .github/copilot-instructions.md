<!-- EpiWatch - Disease Outbreak Detection System -->
# Copilot Instructions for EpiWatch

## Project Overview
EpiWatch is a production-grade AI system for early disease outbreak detection through real-time monitoring of online sources.

## Architecture
- **Backend**: FastAPI with PostgreSQL and Redis
- **Frontend**: React with interactive maps
- **Mobile**: Android app (Kotlin) with push notifications  
- **AI Pipeline**: NLP + anomaly detection with Prophet
- **Data**: Real-time ingestion from RSS/news sources

## Coding Standards
- Use type hints and proper error handling
- Implement comprehensive logging
- Follow modular, testable architecture
- Use .env files for configuration
- Add docstrings for all functions
- Implement proper authentication and security

## Progress Checklist
- [x] Verify copilot-instructions.md exists
- [x] Scaffold EpiWatch project structure
- [x] Set up Python environment and dependencies
- [x] Create data ingestion service
- [x] Build NLP pipeline
- [x] Develop ETL and aggregation
- [x] Build anomaly detection system
- [x] Create FastAPI backend
- [x] Enhance backend with mobile app requirements:
  - [x] Add 233 country coordinates database
  - [x] Implement realistic daily data simulation
  - [x] Add city-level location extraction
  - [x] Create contextual alert descriptions
- [x] Develop HTML dashboard prototype
- [ ] Build React frontend (HTML prototype complete)
- [ ] Build Android mobile app
- [ ] Set up Docker and CI/CD
- [ ] Add testing framework (test scripts created)