"""
API Coverage Analysis - What's Available vs What's Possible
"""

import pandas as pd
from pathlib import Path
import json

def analyze_api_coverage():
    """Analyze what data the API exposes vs what's available"""
    
    print("=" * 80)
    print("🔍 EpiWatch API - Data Coverage Analysis")
    print("=" * 80)
    
    # Load all available data
    results_dir = Path("results")
    
    # 1. Available aggregated data
    print("\n📊 AVAILABLE DATA FILES:")
    print("-" * 80)
    
    available_files = {
        'disease_country_year': results_dir / "disease_country_year_aggregates.csv",
        'disease_year': results_dir / "disease_year_global_aggregates.csv",
        'country_year': results_dir / "country_year_aggregates.csv",
        'region_year': results_dir / "region_year_aggregates.csv",
        'high_risk': results_dir / "high_risk_combinations.csv"
    }
    
    datasets = {}
    for name, path in available_files.items():
        if path.exists():
            df = pd.read_csv(path)
            datasets[name] = df
            print(f"✅ {name:30} - {len(df):,} records")
        else:
            print(f"❌ {name:30} - NOT FOUND")
    
    # 2. Anomaly detection results
    anomaly_dir = results_dir / "anomaly_detection"
    if anomaly_dir.exists():
        anomaly_files = list(anomaly_dir.glob("*_anomalies.csv"))
        alert_files = list(anomaly_dir.glob("*_alerts.json"))
        forecast_files = list(anomaly_dir.glob("*_forecast.csv"))
        
        print(f"\n✅ Anomaly Detection Data:")
        print(f"   • {len(anomaly_files)} anomaly files")
        print(f"   • {len(alert_files)} alert files")
        print(f"   • {len(forecast_files)} forecast files")
    
    # 3. What API currently exposes
    print("\n\n🌐 CURRENT API ENDPOINTS:")
    print("-" * 80)
    
    api_endpoints = {
        '/health': '✅ Health check',
        '/statistics': '✅ Dashboard stats (total outbreaks, diseases, countries)',
        '/alerts': '✅ Recent anomaly alerts (severity, location, disease)',
        '/trends': '✅ 7-day disease trends (simulated from yearly data)',
        '/map': '✅ Geographic outbreak data (10 countries only)',
        '/diseases': '✅ List of all diseases',
        '/feedback': '✅ User feedback submission'
    }
    
    for endpoint, desc in api_endpoints.items():
        print(f"{endpoint:20} - {desc}")
    
    # 4. What's MISSING from API
    print("\n\n❌ DATA NOT EXPOSED BY API (But Available!):")
    print("-" * 80)
    
    missing_features = {
        '🌍 Regional Analysis': [
            'Regional outbreak trends over time',
            'UN region comparisons',
            'WHO region statistics',
            'Regional risk scores'
        ],
        '🎯 High-Risk Combinations': [
            'Disease-Country risk rankings',
            'Historical outbreak patterns',
            'Recurring outbreak locations',
            'Risk trend analysis'
        ],
        '📈 Advanced Forecasting': [
            'Prophet forecast confidence intervals',
            'Multi-year predictions',
            'Seasonal patterns',
            'Forecast accuracy metrics'
        ],
        '🔬 ML Model Insights': [
            'Anomaly detection parameters',
            'Z-scores and statistical metrics',
            'Model performance statistics',
            'Feature importance'
        ],
        '📊 Detailed Analytics': [
            'Year-over-year growth rates',
            'Disease clustering analysis',
            'Country vulnerability scores',
            'Outbreak duration patterns'
        ],
        '🗺️ Geographic Intelligence': [
            'Only 10 countries have coordinates',
            'Missing: 223 other countries',
            'No city-level data',
            'No proximity analysis'
        ]
    }
    
    for category, items in missing_features.items():
        print(f"\n{category}")
        for item in items:
            print(f"   • {item}")
    
    # 5. Specific dataset insights not in API
    print("\n\n💡 DATASET INSIGHTS NOT IN API:")
    print("-" * 80)
    
    if 'disease_country_year' in datasets:
        dcy = datasets['disease_country_year']
        
        # Disease diversity per country
        disease_diversity = dcy.groupby('Country')['Disease'].nunique().sort_values(ascending=False)
        print(f"\n🦠 Disease Diversity Analysis:")
        print(f"   Countries with most disease types:")
        for country, count in disease_diversity.head(5).items():
            print(f"      • {country}: {count} different diseases")
        
        # Outbreak persistence
        outbreak_years = dcy.groupby(['Disease', 'Country'])['Year'].agg(['min', 'max', 'count'])
        outbreak_years['duration'] = outbreak_years['max'] - outbreak_years['min'] + 1
        persistent = outbreak_years[outbreak_years['count'] >= 5].sort_values('count', ascending=False)
        
        print(f"\n⏱️  Persistent Outbreaks (5+ years):")
        print(f"   Top disease-country combinations by duration:")
        for idx, row in persistent.head(5).iterrows():
            disease, country = idx
            print(f"      • {disease} in {country}: {int(row['count'])} years ({int(row['min'])}-{int(row['max'])})")
    
    if 'region_year' in datasets:
        ry = datasets['region_year']
        
        # Regional trends
        latest_year = ry['Year'].max()
        latest_regional = ry[ry['Year'] == latest_year].sort_values('total_outbreaks', ascending=False)
        
        print(f"\n🗺️  Regional Trends ({latest_year}):")
        for _, row in latest_regional.iterrows():
            print(f"      • {row['region']}: {int(row['total_outbreaks'])} outbreaks, {int(row['unique_diseases'])} diseases, {int(row['countries_affected'])} countries")
    
    if 'high_risk' in datasets:
        hr = datasets['high_risk']
        
        # Multi-year patterns
        multi_year = hr[hr['years_affected'] >= 5].nlargest(5, 'total_outbreaks')
        
        print(f"\n🔴 Chronic High-Risk Patterns:")
        for _, row in multi_year.iterrows():
            print(f"      • {row['Disease']} × {row['Country']}: {int(row['total_outbreaks'])} outbreaks over {int(row['years_affected'])} years")
    
    # 6. Recommendations
    print("\n\n✨ RECOMMENDED API ENHANCEMENTS:")
    print("-" * 80)
    
    recommendations = [
        "GET /api/v1/regions - Regional outbreak statistics and trends",
        "GET /api/v1/regions/{region}/diseases - Top diseases by region",
        "GET /api/v1/high-risk - High-risk disease-country combinations",
        "GET /api/v1/forecasts/{disease} - Prophet forecasts with confidence intervals",
        "GET /api/v1/countries/{iso3}/history - Country outbreak history",
        "GET /api/v1/diseases/{disease}/countries - Countries affected by disease",
        "GET /api/v1/analytics/diversity - Disease diversity by country",
        "GET /api/v1/analytics/persistence - Long-term outbreak patterns",
        "GET /api/v1/analytics/growth - Year-over-year growth rates",
        "GET /api/v1/model/metrics - ML model performance metrics"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i:2}. {rec}")
    
    # 7. Summary
    print("\n\n📋 SUMMARY:")
    print("-" * 80)
    print(f"✅ Current API Coverage: ~30%")
    print(f"❌ Unused Dataset Insights: ~70%")
    print(f"📊 Available but not exposed:")
    print(f"   • {len(datasets.get('high_risk', []))} high-risk combinations")
    print(f"   • {len(datasets.get('region_year', []))} regional aggregates")
    print(f"   • {len(anomaly_files) if 'anomaly_files' in locals() else 0} anomaly detection results")
    print(f"   • {len(forecast_files) if 'forecast_files' in locals() else 0} Prophet forecasts")
    
    print(f"\n💡 The API is functional but exposes only basic stats!")
    print(f"   Consider adding the recommended endpoints to unlock full dataset insights.")
    
    return datasets


if __name__ == "__main__":
    analyze_api_coverage()
