#!/usr/bin/env python3
"""
Test script to verify Kubernetes and OCI connectivity
"""
import asyncio
import os
import sys
import traceback
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.kubernetes_service_working import WorkingKubernetesService
from app.services.cloud_service import OCIService

async def test_kubernetes():
    """Test Kubernetes connectivity"""
    print("🔍 Testing Kubernetes Configuration...")
    try:
        k8s_service = WorkingKubernetesService()
        
        if k8s_service.is_configured:
            print("✅ Kubernetes service is configured!")
            
            # Test getting cluster info
            cluster_info = k8s_service.get_cluster_info()
            print(f"   📊 Cluster: {cluster_info.name}")
            print(f"   🌐 Server: {cluster_info.server}")
            print(f"   📦 Nodes: {cluster_info.node_count}")
            print(f"   🏠 Namespaces: {cluster_info.namespace_count}")
            
            # Test RBAC data
            roles = k8s_service.get_rbac_roles()
            bindings = k8s_service.get_rbac_bindings()
            print(f"   🔐 RBAC Roles: {len(roles)}")
            print(f"   🔗 RBAC Bindings: {len(bindings)}")
            
            return True
        else:
            print("❌ Kubernetes service is not configured")
            return False
            
    except Exception as e:
        print(f"❌ Kubernetes test failed: {e}")
        traceback.print_exc()
        return False

async def test_oci():
    """Test OCI connectivity"""
    print("\n🔍 Testing OCI Configuration...")
    try:
        oci_service = OCIService()
        
        if oci_service.oci_available:
            print("✅ OCI service is available!")
            
            # Test getting compartments (this should work)
            try:
                identity_client = oci_service.clients.get('identity')
                if identity_client:
                    # Try to list compartments in root tenancy
                    print("   📋 Testing compartment access...")
                    response = identity_client.list_compartments(
                        compartment_id=oci_service.tenancy_id,
                        limit=5
                    )
                    print(f"   ✅ Found {len(response.data)} compartments")
                    for comp in response.data[:3]:
                        print(f"      - {comp.name} ({comp.lifecycle_state})")
                else:
                    print("   ⚠️ Identity client not available")
            except Exception as e:
                print(f"   ⚠️ Compartment access test failed: {e}")
            
            # Test IAM policies (this might fail)
            try:
                print("   🔒 Testing IAM policy access...")
                response = identity_client.list_policies(
                    compartment_id=oci_service.tenancy_id,
                    limit=5
                )
                print(f"   ✅ Found {len(response.data)} policies")
            except Exception as e:
                print(f"   ❌ IAM policy access failed: {e}")
                print("   💡 This might be a permission issue - try using a compartment OCID instead of tenancy")
            
            return True
        else:
            print("❌ OCI service is not available")
            return False
            
    except Exception as e:
        print(f"❌ OCI test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🧪 GenAI CloudOps - Connectivity Test")
    print("=" * 50)
    
    k8s_ok = await test_kubernetes()
    oci_ok = await test_oci()
    
    print("\n📊 Test Summary:")
    print(f"   Kubernetes: {'✅ Ready' if k8s_ok else '❌ Needs Config'}")
    print(f"   OCI: {'✅ Ready' if oci_ok else '❌ Needs Config'}")
    
    if k8s_ok and oci_ok:
        print("\n🎉 All services are ready! Access Analyzer should work properly.")
    elif k8s_ok:
        print("\n⚠️ Kubernetes ready, but OCI needs configuration. RBAC analysis will work.")
    elif oci_ok:
        print("\n⚠️ OCI ready, but Kubernetes needs configuration. IAM analysis will work.")
    else:
        print("\n❌ Both services need configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 