#!/usr/bin/env python3
"""
Test Cost Analyzer API Integration
Verify that the cost analyzer endpoints are properly integrated with FastAPI
"""

import sys
import json
from fastapi.testclient import TestClient

def test_api_integration():
    """Test the cost analyzer API integration"""
    print("🧪 Testing Cost Analyzer API Integration...")
    
    try:
        # Import the main app
        from main import app
        print("✅ Main app imported successfully")
        
        # Create test client
        client = TestClient(app)
        print("✅ Test client created")
        
        # Test if cost routes are registered in OpenAPI
        print("\n📋 Checking API routes...")
        openapi = client.get("/openapi.json")
        if openapi.status_code == 200:
            routes = openapi.json()
            cost_routes = [path for path in routes.get("paths", {}).keys() if "/cost" in path]
            print(f"✅ Cost routes found: {len(cost_routes)} routes")
            for route in cost_routes:
                print(f"   - {route}")
        else:
            print(f"❌ OpenAPI failed: {openapi.status_code}")
            return False
        
        # Test health endpoint
        print("\n🏥 Testing health endpoint...")
        response = client.get("/api/v1/cost/health")
        print(f"Health endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Cost health endpoint working")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   AI Available: {health_data.get('ai_service_available', False)}")
            print(f"   OCI Available: {health_data.get('oci_billing_available', False)}")
        else:
            print(f"❌ Health endpoint failed: {response.text}")
            return False
            
        # Test API root to see if cost is listed
        print("\n🌐 Testing API root...")
        root_response = client.get("/api/v1/")
        if root_response.status_code == 200:
            root_data = root_response.json()
            endpoints = root_data.get("endpoints", {})
            features = root_data.get("features", [])
            
            if "cost" in endpoints:
                print("✅ Cost endpoint listed in API root")
                print(f"   Cost endpoint: {endpoints['cost']}")
            else:
                print("❌ Cost endpoint not found in API root")
                
            if "cost-optimization" in features:
                print("✅ Cost optimization feature listed")
            else:
                print("❌ Cost optimization feature not listed")
        
        # Test top costly resources endpoint (should require auth)
        print("\n💰 Testing top costly resources endpoint...")
        top_response = client.get("/api/v1/cost/top")
        print(f"Top resources endpoint status: {top_response.status_code}")
        if top_response.status_code == 401:
            print("✅ Authentication required (as expected)")
        elif top_response.status_code == 422:
            print("✅ Endpoint accessible (validation error expected without auth)")
        else:
            print(f"   Response: {top_response.text}")
        
        # Test cost analysis endpoint (should require auth)
        print("\n📊 Testing cost analysis endpoint...")
        analysis_response = client.post("/api/v1/cost/analyze", json={})
        print(f"Analysis endpoint status: {analysis_response.status_code}")
        if analysis_response.status_code == 401:
            print("✅ Authentication required (as expected)")
        elif analysis_response.status_code == 422:
            print("✅ Endpoint accessible (validation error expected without auth)")
        else:
            print(f"   Response: {analysis_response.text}")
        
        print("\n🎉 API integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_integration()
    exit(0 if success else 1) 