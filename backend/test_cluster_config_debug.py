#!/usr/bin/env python3
"""
Debug cluster configuration to see exactly where the error occurs
"""

import requests
import json

BASE_URL = "http://localhost:8000"
KUBECONFIG_PATH = r"C:\Users\2375603\.kube\config"

def debug_cluster_configuration():
    """Debug the cluster configuration step by step"""
    print("🔍 DEBUGGING CLUSTER CONFIGURATION")
    print("=" * 60)
    
    # Step 1: Get auth token
    print("1️⃣ Getting authentication token...")
    try:
        login_data = {"username": "admin", "password": "AdminPass123!"}
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ Authentication successful!")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Read kubeconfig
    print("\n2️⃣ Reading kubeconfig...")
    try:
        with open(KUBECONFIG_PATH, 'r') as f:
            kubeconfig_content = f.read()
        print(f"✅ Kubeconfig loaded: {len(kubeconfig_content)} characters")
    except Exception as e:
        print(f"❌ Failed to read kubeconfig: {e}")
        return
    
    # Step 3: Test individual API endpoints first
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n3️⃣ Testing Kubernetes service health...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/kubernetes/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data.get('status')}")
            print(f"   Clusters configured: {data.get('clusters_configured', 0)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Step 4: Try cluster configuration with detailed error info
    print("\n4️⃣ Attempting cluster configuration...")
    try:
        config_data = {
            "kubeconfig_content": kubeconfig_content,
            "cluster_name": "oke-cluster"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/kubernetes/configure-cluster",
            headers=headers,
            json=config_data,
            timeout=60
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cluster configured successfully!")
            print(f"   Details: {result}")
        else:
            print(f"❌ Configuration failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw response: {response.text}")
                
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_version_api_directly():
    """Test if we can call the Kubernetes API directly to isolate the issue"""
    print("\n🔧 TESTING VERSION API DIRECTLY")
    print("=" * 60)
    
    try:
        from kubernetes import client, config
        import tempfile
        import os
        
        # Read kubeconfig
        with open(KUBECONFIG_PATH, 'r') as f:
            kubeconfig_content = f.read()
        
        # Create temp file and load config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(kubeconfig_content)
            temp_path = f.name
        
        config.load_kube_config(config_file=temp_path)
        
        # Test VersionApi directly
        print("📋 Testing VersionApi...")
        version_api = client.VersionApi()
        version_info = version_api.get_code()
        print(f"✅ Version API works: {version_info.major}.{version_info.minor}")
        
        # Test CoreV1Api
        print("📋 Testing CoreV1Api...")
        core_v1 = client.CoreV1Api()
        nodes = core_v1.list_node()
        print(f"✅ CoreV1 API works: {len(nodes.items)} nodes")
        
        # Cleanup
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Direct API test failed: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        return False

def main():
    print("🚀 CLUSTER CONFIGURATION DEBUG")
    print("=" * 70)
    
    # First test the APIs directly
    direct_success = test_version_api_directly()
    
    # Then test via our service
    service_success = debug_cluster_configuration()
    
    print(f"\n📊 DEBUG SUMMARY")
    print("=" * 70)
    print(f"Direct Kubernetes API: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"Service configuration: {'✅ SUCCESS' if service_success else '❌ FAILED'}")
    
    if direct_success and not service_success:
        print("\n💡 The Kubernetes API works directly but fails through our service.")
        print("   This suggests an issue in our service implementation or server state.")

if __name__ == "__main__":
    main() 