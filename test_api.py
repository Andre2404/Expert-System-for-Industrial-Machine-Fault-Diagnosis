"""
Test API endpoints
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_endpoints():
    print("=" * 60)
    print("Testing API Endpoints")
    print("=" * 60)
    
    # Test 1: Symptoms endpoint
    print("\n1. Testing /api/symptoms")
    try:
        response = requests.get(f'{BASE_URL}/api/symptoms')
        print(f"Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"✅ Success - Found {len(data.get('data', []))} symptoms")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Make sure the Flask server is running!")
        return
    
    # Test 2: Diagnose endpoint
    print("\n2. Testing /api/diagnose with Q2, Q8")
    try:
        response = requests.post(
            f'{BASE_URL}/api/diagnose',
            json={'symptoms': ['Q2', 'Q8']},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            diagnoses = data.get('data', {}).get('diagnoses', [])
            print(f"✅ Success - Found {len(diagnoses)} diagnosis(es)")
            if diagnoses:
                top = diagnoses[0]
                print(f"   Top: {top.get('name')} ({top.get('confidence')}%)")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Rules endpoint
    print("\n3. Testing /api/rules")
    try:
        response = requests.get(f'{BASE_URL}/api/rules')
        print(f"Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"✅ Success - Found {len(data.get('data', []))} rules")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_endpoints()

