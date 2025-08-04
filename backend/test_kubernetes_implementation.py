#!/usr/bin/env python3
"""
Test script for Kubernetes implementation (Task 14)
This will test the Kubernetes service without real cluster connection
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_kubernetes_service_basic():
    """Test basic Kubernetes service functionality"""
    print("Testing Kubernetes Implementation (Task 14)")
    print("=" * 50)
    
    # Test health endpoint (no auth required)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/kubernetes/health", timeout=5)
        print(f"Kubernetes Health: {response.status_code} - {'PASS' if response.status_code == 200 else 'FAIL'}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Clusters Configured: {data.get('clusters_configured', 0)}")
    except Exception as e:
        print(f"Kubernetes Health: ERROR - {e}")
    
    # Test protected endpoints (should return 401 without auth)
    protected_endpoints = [
        "/api/v1/kubernetes/cluster-info",
        "/api/v1/kubernetes/namespaces", 
        "/api/v1/kubernetes/pods",
        "/api/v1/kubernetes/rbac/roles",
        "/api/v1/kubernetes/rbac/bindings",
        "/api/v1/kubernetes/pods/status-summary"
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "PASS (AUTH PROTECTED)" if response.status_code == 401 else f"Status: {response.status_code}"
            print(f"{endpoint}: {status}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

def test_api_documentation_includes_kubernetes():
    """Test that API documentation includes Kubernetes endpoints"""
    print("\nTesting API Documentation Update")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/", timeout=5)
        print(f"API Root: {response.status_code} - {'PASS' if response.status_code == 200 else 'FAIL'}")
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', {})
            microservices = data.get('microservices', {})
            
            # Check if kubernetes is listed
            if 'kubernetes' in endpoints:
                print(f"   Kubernetes Endpoint: {endpoints['kubernetes']} - FOUND")
            else:
                print("   Kubernetes Endpoint: NOT FOUND")
            
            if 'kubernetes' in microservices:
                print(f"   Kubernetes Microservice: {microservices['kubernetes']}")
            else:
                print("   Kubernetes Microservice: NOT FOUND")
                
    except Exception as e:
        print(f"API Root: ERROR - {e}")

def test_openapi_docs():
    """Test OpenAPI documentation includes Kubernetes"""
    print("\nTesting OpenAPI Documentation")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"API Docs: {response.status_code} - {'PASS' if response.status_code == 200 else 'FAIL'}")
        
        # Test OpenAPI JSON
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            
            k8s_paths = [path for path in paths.keys() if '/kubernetes/' in path]
            print(f"   Kubernetes Endpoints Found: {len(k8s_paths)}")
            if k8s_paths:
                print(f"   Sample Endpoint: {k8s_paths[0]}")
        
    except Exception as e:
        print(f"OpenAPI Docs: ERROR - {e}")

def main():
    print("KUBERNETES IMPLEMENTATION TESTING")
    print("=" * 60)
    print("Testing Task 14: Kubernetes Client Integration")
    print("=" * 60)
    
    test_kubernetes_service_basic()
    test_api_documentation_includes_kubernetes()
    test_openapi_docs()
    
    print("\n" + "=" * 60)
    print("BASIC TESTING COMPLETE!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. The Kubernetes service is ready for real cluster connection")
    print("2. Provide kubeconfig to test with real OKE cluster")
    print("3. Test RBAC analysis and pod monitoring features")
    print("4. Verify integration with Tasks 15 and 17")
    
    print("\nKubeconfig can be provided via:")
    print("- API endpoint: POST /api/v1/kubernetes/configure-cluster")
    print("- File upload: POST /api/v1/kubernetes/upload-kubeconfig")

if __name__ == "__main__":
    main() 