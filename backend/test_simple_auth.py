#!/usr/bin/env python3
"""
Simple authentication test to isolate the TypeError
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_minimal_registration():
    """Test with minimal data to isolate the error"""
    print("🔍 MINIMAL AUTHENTICATION TEST")
    print("=" * 50)
    
    # Test with admin user (should exist from init_db.py)
    print("1. Testing login with default admin user...")
    try:
        login_data = {"username": "admin", "password": "AdminPass123!"}
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=10)
        print(f"   Admin login: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"   ✅ Admin login successful! Token: {token[:20] if token else 'None'}...")
            return token
        else:
            print(f"   ❌ Admin login failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Admin login error: {e}")
    
    # Test user creation with very minimal data
    print("\n2. Testing simple user creation...")
    simple_user = {
        "username": "simpleuser",
        "email": "simple@test.com", 
        "password": "Simple123",  # Fixed to match password requirements
        "full_name": "Simple User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=simple_user, timeout=10)
        print(f"   Registration: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ User created successfully!")
            
            # Try to login with new user
            login_data = {"username": "simpleuser", "password": "Simple123"}
            login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=10)
            print(f"   Login: {login_response.status_code}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data.get("access_token")
                print(f"   ✅ Login successful! Token: {token[:20] if token else 'None'}...")
                return token
        else:
            print(f"   ❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
    
    return None

def test_kubernetes_with_admin():
    """Test Kubernetes endpoints using admin credentials"""
    print("\n3. Testing with admin credentials...")
    try:
        login_data = {"username": "admin", "password": "AdminPass123!"}
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test Kubernetes health
            k8s_response = requests.get(f"{BASE_URL}/api/v1/kubernetes/health", timeout=5)
            print(f"   K8s Health: {k8s_response.status_code}")
            
            # Test protected endpoint
            cluster_response = requests.get(f"{BASE_URL}/api/v1/kubernetes/cluster-info", headers=headers, timeout=5)
            print(f"   K8s Cluster Info: {cluster_response.status_code}")
            
            if cluster_response.status_code == 400:
                print("   ✅ Auth working, ready for cluster configuration!")
                return token
            elif cluster_response.status_code == 200:
                print("   ✅ Cluster already configured!")
                return token
            else:
                print(f"   Response: {cluster_response.text}")
                
    except Exception as e:
        print(f"   ❌ Admin test error: {e}")
    
    return None

def main():
    print("🧪 SIMPLE AUTHENTICATION ISOLATION TEST")
    print("=" * 60)
    
    # Try to get a working token
    token = test_minimal_registration()
    
    if not token:
        token = test_kubernetes_with_admin()
    
    if token:
        print(f"\n✅ SUCCESS!")
        print(f"Authentication working with token: {token[:30]}...")
        print(f"\nYou can now configure Kubernetes cluster:")
        print(f"Ready to proceed with Task 14 Kubernetes integration!")
    else:
        print(f"\n❌ FAILURE!")
        print("Authentication still not working.")
        print("Recommend:")
        print("1. Check backend logs for detailed error information")
        print("2. Verify database initialization completed successfully")
        print("3. Check password requirements (uppercase, lowercase, digit, 8+ chars)")

if __name__ == "__main__":
    main() 