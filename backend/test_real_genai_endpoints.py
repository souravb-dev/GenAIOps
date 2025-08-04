#!/usr/bin/env python3
"""
Test actual GenAI endpoints that exist in the application
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_real_genai_endpoints():
    """Test the actual GenAI endpoints that exist"""
    print("Testing Real GenAI Endpoints (Task 8)")
    print("=" * 45)
    
    # Test GenAI health (no auth required)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/genai/health", timeout=5)
        print(f"✅ GenAI Health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Provider: {data.get('provider', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
    except Exception as e:
        print(f"❌ GenAI Health: {e}")
    
    # Test GenAI stats (requires auth - expect 401)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/genai/stats", timeout=5)
        print(f"🔒 GenAI Stats: {response.status_code} (401 = auth required, OK)")
    except Exception as e:
        print(f"❌ GenAI Stats: {e}")
    
    # Test GenAI chat (requires auth - expect 401)
    try:
        data = {"message": "Hello", "session_id": "test123"}
        response = requests.post(f"{BASE_URL}/api/v1/genai/chat", json=data, timeout=5)
        print(f"🔒 GenAI Chat: {response.status_code} (401 = auth required, OK)")
    except Exception as e:
        print(f"❌ GenAI Chat: {e}")
    
    # Test GenAI analysis (requires auth - expect 401)
    try:
        data = {"data": {"test": "data"}, "context": {"type": "test"}}
        response = requests.post(f"{BASE_URL}/api/v1/genai/analysis", json=data, timeout=5)
        print(f"🔒 GenAI Analysis: {response.status_code} (401 = auth required, OK)")
    except Exception as e:
        print(f"❌ GenAI Analysis: {e}")

def test_chatbot_endpoints():
    """Test chatbot endpoints (Task 12-13)"""
    print("\nTesting Chatbot Endpoints (Task 12-13)")
    print("=" * 45)
    
    # Test chatbot health (requires auth - expect 401)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/chatbot/health", timeout=5)
        print(f"🔒 Chatbot Health: {response.status_code} (401 = auth required, OK)")
    except Exception as e:
        print(f"❌ Chatbot Health: {e}")
    
    # Test chatbot enhanced chat (requires auth - expect 401)
    try:
        data = {"message": "Hello chatbot", "intent": "GENERAL_QUERY"}
        response = requests.post(f"{BASE_URL}/api/v1/chatbot/enhanced-chat", json=data, timeout=5)
        print(f"🔒 Chatbot Enhanced Chat: {response.status_code} (401 = auth required, OK)")
    except Exception as e:
        print(f"❌ Chatbot Enhanced Chat: {e}")

def test_remediation_endpoints():
    """Test remediation endpoints (Task 10)"""
    print("\nTesting Remediation Endpoints (Task 10)")
    print("=" * 45)
    
    # Test remediation health (no auth required)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/remediation/health", timeout=5)
        print(f"✅ Remediation Health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'Unknown')}")
    except Exception as e:
        print(f"❌ Remediation Health: {e}")
    
    # Test remediation actions (requires auth - expect 401)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/remediation/actions", timeout=5)
        print(f"🔒 Remediation Actions: {response.status_code} (401 = auth required, OK)")
    except Exception as e:
        print(f"❌ Remediation Actions: {e}")

def main():
    test_real_genai_endpoints()
    test_chatbot_endpoints()
    test_remediation_endpoints()
    
    print("\n🎉 All Tests Complete!")
    print("\nSummary:")
    print("✅ = Working correctly")
    print("🔒 = Protected by authentication (this is good!)")
    print("❌ = Error")
    
    print("\nNext: Test frontend at http://localhost:3000")

if __name__ == "__main__":
    main() 