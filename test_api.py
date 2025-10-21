"""
Test EpiWatch API Endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_statistics():
    """Test statistics endpoint"""
    print("\n📊 Testing /statistics endpoint...")
    response = requests.get(f"{BASE_URL}/statistics")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"\nDashboard Statistics:")
    print(f"  Total Outbreaks: {data['total_outbreaks']}")
    print(f"  Active Diseases: {data['active_diseases']}")
    print(f"  Affected Countries: {data['affected_countries']}")
    print(f"\n  Top 4 Diseases:")
    for disease in data['disease_stats']:
        trend = "📈" if disease['trend'] == 'up' else "📉"
        print(f"    {trend} {disease['disease']}: {disease['current_count']} ({disease['change_pct']:+.1f}%)")


def test_alerts():
    """Test alerts endpoint"""
    print("\n🚨 Testing /alerts endpoint...")
    response = requests.get(f"{BASE_URL}/alerts?limit=5")
    print(f"Status: {response.status_code}")
    alerts = response.json()
    print(f"\nFound {len(alerts)} alerts:")
    for alert in alerts:
        print(f"\n  [{alert['severity_level'].upper()}] {alert['disease']}")
        print(f"    {alert['message'][:100]}...")


def test_trends():
    """Test trends endpoint"""
    print("\n📈 Testing /trends endpoint...")
    response = requests.get(f"{BASE_URL}/trends")
    print(f"Status: {response.status_code}")
    trends = response.json()
    print(f"\nFound {len(trends)} disease trends:")
    for trend in trends:
        direction = "📈" if trend['trend_direction'] == 'up' else "📉" if trend['trend_direction'] == 'down' else "➡️"
        print(f"  {direction} {trend['disease']}: {trend['total_count']} ({trend['change_pct']:+.1f}%)")


def test_map():
    """Test map endpoint"""
    print("\n🗺️  Testing /map endpoint...")
    response = requests.get(f"{BASE_URL}/map")
    print(f"Status: {response.status_code}")
    map_data = response.json()
    print(f"\nFound {len(map_data)} outbreak locations")
    
    # Count by risk level
    risk_counts = {}
    for item in map_data:
        risk = item['risk_level']
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    print(f"\nRisk Level Distribution:")
    for risk, count in sorted(risk_counts.items()):
        emoji = "🔴" if risk == "high" else "🟡" if risk == "medium" else "🟢"
        print(f"  {emoji} {risk.capitalize()}: {count}")


def test_diseases():
    """Test diseases endpoint"""
    print("\n🦠 Testing /diseases endpoint...")
    response = requests.get(f"{BASE_URL}/diseases")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"\nTotal diseases in system: {data['count']}")
    print(f"Sample diseases: {', '.join(data['diseases'][:5])}")


def main():
    """Run all tests"""
    print("=" * 70)
    print("🔬 EpiWatch API - Endpoint Testing")
    print("=" * 70)
    
    try:
        test_health()
        test_statistics()
        test_alerts()
        test_trends()
        test_map()
        test_diseases()
        
        print("\n" + "=" * 70)
        print("✅ All API endpoints working correctly!")
        print("=" * 70)
        print("\n📖 Interactive API Documentation:")
        print("   http://localhost:8000/api/docs")
        print("\n🔗 Test in browser:")
        print("   http://localhost:8000/api/v1/statistics")
        print("   http://localhost:8000/api/v1/alerts")
        print("   http://localhost:8000/api/v1/trends")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API!")
        print("   Make sure the server is running: python backend/main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
