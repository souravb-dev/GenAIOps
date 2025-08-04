#!/usr/bin/env python3
"""
Test import in server context to debug the issue
"""

import requests
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_server_import():
    """Test what's happening with imports in the server"""
    print("🔍 TESTING SERVER IMPORT CONTEXT")
    print("=" * 50)
    
    try:
        # Test direct import
        print("1. Testing direct kubernetes_working import...")
        from app.api.endpoints import kubernetes_working
        print(f"   ✅ Direct import success: {len(kubernetes_working.router.routes)} routes")
        
        # Test routes module import
        print("2. Testing routes module import...")
        from app.api import routes
        print(f"   ✅ Routes module imported")
        
        # Check if kubernetes_working is in the routes module namespace
        print("3. Checking if kubernetes_working is available in routes...")
        if hasattr(routes, 'kubernetes_working'):
            print("   ✅ kubernetes_working found in routes module")
        else:
            print("   ❌ kubernetes_working NOT found in routes module")
        
        # Test api_router routes
        print("4. Checking api_router routes...")
        api_router = routes.api_router
        route_paths = [route.path for route in api_router.routes if hasattr(route, 'path')]
        k8s_routes = [path for path in route_paths if '/k8s' in path]
        print(f"   Routes with /k8s: {len(k8s_routes)}")
        for route in k8s_routes[:3]:
            print(f"     - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_live_server():
    """Test what the live server is actually serving"""
    print(f"\n🌐 TESTING LIVE SERVER")
    print("=" * 50)
    
    try:
        # Test API root
        response = requests.get("http://localhost:8000/api/v1/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get("endpoints", {})
            print(f"✅ Live server endpoints: {list(endpoints.keys())}")
            
            if 'k8s' in endpoints:
                print("   ✅ k8s endpoint found in live server")
            else:
                print("   ❌ k8s endpoint NOT found in live server")
        else:
            print(f"❌ Failed to get API root: {response.status_code}")
        
        # Test direct k8s health endpoint
        try:
            response = requests.get("http://localhost:8000/api/v1/k8s/health", timeout=5)
            print(f"✅ /k8s/health direct test: {response.status_code}")
        except Exception as e:
            print(f"❌ /k8s/health direct test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Live server test failed: {e}")
        return False

def main():
    print("🚨 KUBERNETES WORKING ENDPOINT DEBUG")
    print("=" * 60)
    
    import_success = test_server_import()
    server_success = test_live_server()
    
    if import_success and server_success:
        print(f"\n💡 DIAGNOSIS:")
        print("The import works but the live server doesn't have the routes.")
        print("This suggests the server didn't reload the routes properly.")
        print("Try adding a simple print statement to routes.py to force reload.")
    elif not import_success:
        print(f"\n💡 DIAGNOSIS:")
        print("There's an import error preventing the routes from loading.")
    else:
        print(f"\n💡 DIAGNOSIS:")
        print("Mixed results - need further investigation.")

if __name__ == "__main__":
    main() 