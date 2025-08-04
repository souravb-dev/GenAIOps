"""
Quick test script for Access Analyzer fixes
Tests the endpoints to verify they don't timeout
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_auth():
    """Test authentication"""
    login_data = {
        "username": "admin",
        "password": "AdminPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=10)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None

def test_access_analyzer_health(token):
    """Test access analyzer health - should not timeout"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/access/health", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Access Analyzer health check: {data.get('status')}")
            print(f"   Kubernetes: {data.get('kubernetes_available')}")
            print(f"   OCI: {data.get('oci_available')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_kubernetes_health(token):
    """Test kubernetes health - should not timeout"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/kubernetes/working/health", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Kubernetes health check: {data.get('status')}")
            return True
        else:
            print(f"❌ Kubernetes health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Kubernetes health error: {e}")
        return False

def test_rbac_without_cluster(token):
    """Test RBAC analysis without cluster - should return empty gracefully"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/access/rbac", headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RBAC analysis: {data.get('success')} - {data.get('message')}")
            return True
        else:
            print(f"❌ RBAC analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ RBAC analysis error: {e}")
        return False

def test_summary(token):
    """Test summary endpoint - should not return 500"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/access/summary",
            params={"compartment_id": "test-compartment"},
            headers=headers,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Summary endpoint: Working")
            return True
        else:
            print(f"❌ Summary failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Summary error: {e}")
        return False

def main():
    print("🧪 Quick Access Analyzer Test")
    print("=" * 50)
    
    # Test authentication
    token = test_auth()
    if not token:
        return
    
    # Test health checks
    print("\n📋 Health Checks")
    k8s_health = test_kubernetes_health(token)
    access_health = test_access_analyzer_health(token)
    
    # Test RBAC without cluster
    print("\n📋 RBAC Analysis (No Cluster)")
    rbac_result = test_rbac_without_cluster(token)
    
    # Test summary
    print("\n📋 Summary Endpoint")
    summary_result = test_summary(token)
    
    # Results
    print("\n" + "=" * 50)
    print("🎯 Test Results:")
    print(f"   Kubernetes Health: {'✅' if k8s_health else '❌'}")
    print(f"   Access Analyzer Health: {'✅' if access_health else '❌'}")
    print(f"   RBAC Analysis: {'✅' if rbac_result else '❌'}")
    print(f"   Summary Endpoint: {'✅' if summary_result else '❌'}")
    
    success_rate = sum([k8s_health, access_health, rbac_result, summary_result]) / 4 * 100
    print(f"\n🎉 Success Rate: {success_rate:.0f}%")
    
    if success_rate >= 75:
        print("✅ Access Analyzer fixes are working!")
    else:
        print("❌ Some issues remain")

if __name__ == "__main__":
    main() 