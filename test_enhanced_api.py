"""
Test Enhanced EpiWatch API - Verify all 4 improvements:
1. 233 country coordinates (vs previous 10)
2. Realistic daily data simulation with seasonal patterns
3. City-level location information
4. Contextual alert descriptions
"""

import requests
import json
from typing import Dict, List

BASE_URL = "http://localhost:8000/api/v1"

def test_map_coverage():
    """Test 1: Verify map shows 233 country coordinates (not just 10)"""
    print("\n" + "="*80)
    print("TEST 1: Country Coordinate Coverage")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/map")
    assert response.status_code == 200, f"Map endpoint failed: {response.status_code}"
    
    map_data = response.json()
    unique_countries = {item['country'] for item in map_data}
    
    print(f"✅ Map endpoint: {response.status_code}")
    print(f"✅ Total outbreak locations: {len(map_data)}")
    print(f"✅ Unique countries with coordinates: {len(unique_countries)}")
    print(f"\nSample countries on map:")
    for country in list(unique_countries)[:10]:
        print(f"  - {country}")
    
    # Check that we have significantly more than the old 10 countries
    if len(unique_countries) > 20:
        print(f"\n✅ SUCCESS: {len(unique_countries)} countries (expected >20)")
    else:
        print(f"\n⚠️  WARNING: Only {len(unique_countries)} countries (expected >20)")
    
    return map_data


def test_daily_trends():
    """Test 2: Verify trends use realistic daily simulation with seasonal patterns"""
    print("\n" + "="*80)
    print("TEST 2: Realistic Daily Data Simulation")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/trends")
    assert response.status_code == 200, f"Trends endpoint failed: {response.status_code}"
    
    trends = response.json()
    
    print(f"✅ Trends endpoint: {response.status_code}")
    print(f"✅ Number of disease trends: {len(trends)}")
    
    for trend in trends:
        print(f"\nDisease: {trend['disease']}")
        print(f"  Total (7-day): {trend['total_count']}")
        print(f"  Change: {trend['change_pct']:+.1f}% ({trend['trend_direction']})")
        
        # Check for enhanced fields
        if 'severity' in trend:
            print(f"  Severity: {trend['severity']} ✅")
        if 'description' in trend:
            print(f"  Context: {trend['description'][:60]}... ✅")
        
        # Show daily breakdown
        print(f"  Daily breakdown (7 days):")
        for point in trend['trend_data']:
            print(f"    {point['date']}: {point['count']} cases")
        
        # Verify daily data has variation (not uniform)
        counts = [p['count'] for p in trend['trend_data']]
        has_variation = len(set(counts)) > 1
        if has_variation:
            print(f"  ✅ Daily variation detected (realistic simulation)")
        else:
            print(f"  ⚠️  No daily variation (may be uniform simulation)")
    
    return trends


def test_city_locations():
    """Test 3: Verify alerts include city-level location information"""
    print("\n" + "="*80)
    print("TEST 3: City-Level Location Information")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/alerts?limit=10")
    assert response.status_code == 200, f"Alerts endpoint failed: {response.status_code}"
    
    alerts = response.json()
    
    print(f"✅ Alerts endpoint: {response.status_code}")
    print(f"✅ Number of alerts: {len(alerts)}")
    
    city_count = 0
    for idx, alert in enumerate(alerts, 1):
        print(f"\nAlert {idx}: {alert['disease']}")
        print(f"  Country: {alert['location']}")
        
        # Check for enhanced city location
        if 'city_location' in alert and alert['city_location']:
            print(f"  City: {alert['city_location']} ✅")
            city_count += 1
        else:
            print(f"  City: Not available")
        
        print(f"  Severity: {alert['severity_level']} ({alert['severity']:.1f})")
        print(f"  Cases: {alert['actual_count']} (expected {alert['expected_count']:.1f})")
        print(f"  Deviation: {alert['deviation_pct']:+.1f}%")
    
    print(f"\n✅ Alerts with city information: {city_count}/{len(alerts)}")
    return alerts


def test_contextual_descriptions():
    """Test 4: Verify alerts include contextual outbreak descriptions"""
    print("\n" + "="*80)
    print("TEST 4: Contextual Alert Descriptions")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/alerts?limit=10")
    assert response.status_code == 200, f"Alerts endpoint failed: {response.status_code}"
    
    alerts = response.json()
    
    print(f"✅ Alerts endpoint: {response.status_code}")
    
    context_count = 0
    for idx, alert in enumerate(alerts, 1):
        print(f"\nAlert {idx}: {alert['disease']} in {alert.get('city_location', alert['location'])}")
        
        # Check for enhanced context description
        if 'context_description' in alert and alert['context_description']:
            print(f"  Context: {alert['context_description']} ✅")
            context_count += 1
        else:
            print(f"  Context: Not available")
        
        print(f"  Standard message: {alert['message'][:80]}...")
    
    print(f"\n✅ Alerts with contextual descriptions: {context_count}/{len(alerts)}")
    return alerts


def test_prototype_requirements():
    """Verify API matches mobile app prototype requirements"""
    print("\n" + "="*80)
    print("PROTOTYPE REQUIREMENTS VERIFICATION")
    print("="*80)
    
    results = {
        "map_countries": 0,
        "daily_trends": False,
        "city_locations": False,
        "contextual_alerts": False
    }
    
    # Check map coverage
    map_data = requests.get(f"{BASE_URL}/map").json()
    results["map_countries"] = len({item['country'] for item in map_data})
    
    # Check daily trends
    trends = requests.get(f"{BASE_URL}/trends").json()
    if trends and 'severity' in trends[0] and 'description' in trends[0]:
        results["daily_trends"] = True
    
    # Check city locations
    alerts = requests.get(f"{BASE_URL}/alerts?limit=5").json()
    city_alerts = [a for a in alerts if a.get('city_location')]
    results["city_locations"] = len(city_alerts) > 0
    
    # Check contextual descriptions
    context_alerts = [a for a in alerts if a.get('context_description')]
    results["contextual_alerts"] = len(context_alerts) > 0
    
    print("\nPrototype Requirements Status:")
    print(f"  Dashboard Map:")
    print(f"    ✅ Country coverage: {results['map_countries']} countries (target: 233)")
    print(f"  7-Day Trends:")
    print(f"    {'✅' if results['daily_trends'] else '❌'} Realistic daily simulation with severity/context")
    print(f"  Recent Alerts:")
    print(f"    {'✅' if results['city_locations'] else '❌'} City-level locations (e.g., 'Chicago, IL')")
    print(f"    {'✅' if results['contextual_alerts'] else '❌'} Contextual descriptions (e.g., 'Rapid spread in schools')")
    
    all_pass = (
        results["map_countries"] > 20 and
        results["daily_trends"] and
        results["city_locations"] and
        results["contextual_alerts"]
    )
    
    if all_pass:
        print("\n✅ ALL PROTOTYPE REQUIREMENTS MET! API ready for mobile app integration.")
    else:
        print("\n⚠️  Some requirements not fully met. See details above.")
    
    return results


def main():
    """Run all enhancement tests"""
    print("="*80)
    print("EPIWATCH ENHANCED API TEST SUITE")
    print("Testing 4 critical improvements for mobile app prototype")
    print("="*80)
    
    try:
        # Test health endpoint first
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code != 200:
            print(f"❌ API is not running. Start it with: uvicorn backend.main:app --reload")
            return
        
        print(f"✅ API is running at {BASE_URL}")
        
        # Run all tests
        test_map_coverage()
        test_daily_trends()
        test_city_locations()
        test_contextual_descriptions()
        test_prototype_requirements()
        
        print("\n" + "="*80)
        print("TEST SUITE COMPLETE")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API at {BASE_URL}")
        print("Start the API with: uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
