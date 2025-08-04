"""
Minimal test to isolate blocking issues
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_auth():
    """Test authentication"""
    login_data = {
        "username": "admin",
        "password": "AdminPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=5)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None

def test_simple_health():
    """Test simple health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Simple health check successful")
            return True
        else:
            print(f"❌ Simple health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Simple health error: {e}")
        return False

def test_genai_health(token):
    """Test GenAI service health"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/api/v1/genai/health", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ GenAI health check successful")
            return True
        else:
            print(f"❌ GenAI health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GenAI health error: {e}")
        return False

def test_cloud_health(token):
    """Test Cloud service health"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Use the correct test endpoint for cloud service
        response = requests.get(f"{BASE_URL}/api/v1/cloud/test/compartments", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cloud health check successful: {data.get('status')}")
            print(f"   OCI Available: {data.get('oci_available')}")
            print(f"   Compartments Found: {data.get('compartment_count', 0)}")
            return True
        else:
            print(f"❌ Cloud health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cloud health error: {e}")
        return False

def main():
    print("🔍 Minimal Endpoint Test - Isolating Blocking Issues")
    print("=" * 60)
    
    # Test simple endpoints first
    print("\n📋 Basic Health (No Auth)")
    basic_health = test_simple_health()
    
    # Test authentication
    print("\n📋 Authentication")
    token = test_auth()
    if not token:
        return
    
    # Test individual services
    print("\n📋 Service Health Checks")
    genai_health = test_genai_health(token)
    cloud_health = test_cloud_health(token)
    
    print(f"\n🎯 Results:")
    print(f"   Basic Health: {'✅' if basic_health else '❌'}")
    print(f"   GenAI Health: {'✅' if genai_health else '❌'}")
    print(f"   Cloud Health: {'✅' if cloud_health else '❌'}")
    
    if genai_health and cloud_health:
        print("\n✅ Core services working - issue is likely in Kubernetes/Access Analyzer")
    else:
        print("\n❌ Core services have issues - problem is deeper")

if __name__ == "__main__":
    main() 