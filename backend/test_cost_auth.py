#!/usr/bin/env python3
import requests
import json

def test_cost_auth():
    """Test cost analyzer with authentication"""
    
    # Login with correct credentials
    print("🔐 Testing login...")
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', 
                                 json={'username': 'admin', 'password': 'AdminPass123!'})
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        print('✅ Login successful')
        
        # Test cost analyze endpoint
        print("📊 Testing cost analyze endpoint...")
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post('http://localhost:8000/api/v1/cost/analyze',
                               headers=headers,
                               json={
                                   'period': 'monthly',
                                   'include_forecasting': True,
                                   'include_optimization': True,
                                   'include_anomaly_detection': True
                               })
        
        print(f"Cost Analyze Status: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error - Backend issue confirmed!")
            print("Error details:")
            print(response.text)
        elif response.status_code == 200:
            print("✅ Cost analyzer working!")
            result = response.json()
            print(f"Analysis ID: {result.get('analysis_id', 'N/A')}")
        else:
            print(f"Unexpected status: {response.status_code}")
            print(response.text)
            
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)

if __name__ == "__main__":
    test_cost_auth() 