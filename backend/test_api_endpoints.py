#!/usr/bin/env python3
"""
Simple API endpoint testing script for tasks 8-13
Run this after starting the backend server in another terminal
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test basic health check"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_genai_endpoints():
    """Test GenAI integration endpoints (Task 8)"""
    print("\n🧠 Testing GenAI Service Endpoints (Task 8):")
    
    endpoints = [
        "/api/v1/genai/health",
        "/api/v1/genai/models",
        "/api/v1/genai/capabilities"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"   {status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")

def test_monitoring_endpoints():
    """Test Monitoring and Alerts endpoints (Task 7)"""
    print("\n📊 Testing Monitoring Service Endpoints (Task 7):")
    
    endpoints = [
        "/api/v1/monitoring/health",
        "/api/v1/monitoring/test"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"   {status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")

def test_remediation_endpoints():
    """Test Remediation endpoints (Task 10)"""
    print("\n🔧 Testing Remediation Service Endpoints (Task 10):")
    
    endpoints = [
        "/api/v1/remediation/health",
        "/api/v1/remediation/actions"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = "✅" if response.status_code in [200, 401] else "⚠️"  # 401 is OK (needs auth)
            print(f"   {status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")

def test_chatbot_endpoints():
    """Test Chatbot endpoints (Task 12-13)"""
    print("\n💬 Testing Chatbot Service Endpoints (Task 12-13):")
    
    endpoints = [
        "/api/v1/chatbot/health",
        "/api/v1/chatbot/templates"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = "✅" if response.status_code in [200, 401] else "⚠️"  # 401 is OK (needs auth)
            print(f"   {status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")

def main():
    print("🚀 GenAI CloudOps API Testing (Tasks 8-13)")
    print("=" * 50)
    
    # First check if server is running
    if not test_health_endpoint():
        print("\n❌ Server is not running. Please start the backend server first:")
        print("   python main.py")
        return
    
    print("\n🎉 Server is running! Testing specific task endpoints...")
    
    # Test task-specific endpoints
    test_genai_endpoints()
    test_monitoring_endpoints() 
    test_remediation_endpoints()
    test_chatbot_endpoints()
    
    print("\n✅ API Testing Complete!")
    print("\nNext steps:")
    print("1. Start frontend: cd ../frontend && npm run dev")
    print("2. Visit http://localhost:3000 to test the UI")
    print("3. Check API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 