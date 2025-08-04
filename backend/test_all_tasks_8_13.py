#!/usr/bin/env python3
"""
Comprehensive test script for Tasks 8-13 - PowerShell compatible
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_task_8_genai():
    """Test Task 8: GenAI Integration Service"""
    print("Testing Task 8: GenAI Integration Service")
    print("=" * 45)
    
    # Test GenAI health (no auth required)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/genai/health", timeout=5)
        print(f"GenAI Health: {response.status_code} - {'PASS' if response.status_code == 200 else 'FAIL'}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Provider: {data.get('provider', 'Unknown')}")
            print(f"   Service: {data.get('service', 'Unknown')}")
    except Exception as e:
        print(f"GenAI Health: ERROR - {e}")
    
    # Test protected endpoints (should return 401)
    endpoints = [
        ("/api/v1/genai/stats", "GET", None),
        ("/api/v1/genai/chat", "POST", {"message": "Hello", "session_id": "test123"}),
        ("/api/v1/genai/analysis", "POST", {"data": {"test": "data"}, "context": {"type": "test"}})
    ]
    
    for endpoint, method, data in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
            
            status = "PASS (AUTH PROTECTED)" if response.status_code == 401 else f"Status: {response.status_code}"
            print(f"{endpoint}: {status}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

def test_task_10_remediation():
    """Test Task 10: Remediation Panel Backend"""
    print("\nTesting Task 10: Remediation Panel Backend")
    print("=" * 45)
    
    # Test remediation health (no auth required)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/remediation/health", timeout=5)
        print(f"Remediation Health: {response.status_code} - {'PASS' if response.status_code == 200 else 'FAIL'}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Service: {data.get('service', 'Unknown')}")
    except Exception as e:
        print(f"Remediation Health: ERROR - {e}")
    
    # Test protected endpoints
    protected_endpoints = [
        "/api/v1/remediation/actions",
        "/api/v1/remediation/audit-logs"
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "PASS (AUTH PROTECTED)" if response.status_code == 401 else f"Status: {response.status_code}"
            print(f"{endpoint}: {status}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

def test_task_12_13_chatbot():
    """Test Task 12-13: Chatbot Backend and Frontend"""
    print("\nTesting Task 12-13: Chatbot Backend & Frontend")
    print("=" * 45)
    
    # Test chatbot endpoints (all require auth)
    chatbot_endpoints = [
        ("/api/v1/chatbot/health", "GET", None),
        ("/api/v1/chatbot/enhanced-chat", "POST", {"message": "Hello", "intent": "GENERAL_QUERY"}),
        ("/api/v1/chatbot/templates", "GET", None)
    ]
    
    for endpoint, method, data in chatbot_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
            
            status = "PASS (AUTH PROTECTED)" if response.status_code == 401 else f"Status: {response.status_code}"
            print(f"{endpoint}: {status}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

def test_monitoring_alerts():
    """Test Task 7: Monitoring and Alerts (supporting Task 9)"""
    print("\nTesting Task 7: Monitoring & Alerts (supports Task 9)")
    print("=" * 45)
    
    # Test monitoring endpoints
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/test", timeout=5)
        print(f"Monitoring Test: {response.status_code} - {'PASS' if response.status_code == 200 else 'FAIL'}")
    except Exception as e:
        print(f"Monitoring Test: ERROR - {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/health", timeout=5)
        status = "PASS (AUTH PROTECTED)" if response.status_code == 401 else f"Status: {response.status_code}"
        print(f"Monitoring Health: {status}")
    except Exception as e:
        print(f"Monitoring Health: ERROR - {e}")

def test_api_documentation():
    """Test if API documentation is accessible"""
    print("\nTesting API Documentation")
    print("=" * 45)
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"API Documentation: {response.status_code} - {'PASS' if response.status_code == 200 else 'FAIL'}")
    except Exception as e:
        print(f"API Documentation: ERROR - {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/", timeout=5)
        print(f"API Root: {response.status_code} - {'PASS' if response.status_code == 200 else 'FAIL'}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Features: {len(data.get('features', []))} enabled")
            print(f"   Endpoints: {len(data.get('endpoints', {}))} available")
    except Exception as e:
        print(f"API Root: ERROR - {e}")

def main():
    print("COMPREHENSIVE TESTING: Tasks 8-13")
    print("=" * 50)
    print("Backend Server: http://localhost:8000")
    print("Frontend Server: http://localhost:3000")
    print("=" * 50)
    
    test_task_8_genai()
    test_task_10_remediation()
    test_task_12_13_chatbot()
    test_monitoring_alerts()
    test_api_documentation()
    
    print("\n" + "=" * 50)
    print("TESTING COMPLETE!")
    print("=" * 50)
    print("\nResults Summary:")
    print("- PASS: Endpoint working correctly")
    print("- PASS (AUTH PROTECTED): Endpoint requires authentication (correct)")
    print("- FAIL: Endpoint not working")
    print("- ERROR: Connection or other error")
    
    print("\nNext Steps:")
    print("1. Visit http://localhost:3000 to test the frontend")
    print("2. Visit http://localhost:8000/docs for API documentation")
    print("3. Test user registration and login flows")
    print("4. Test the complete application features")

if __name__ == "__main__":
    main() 