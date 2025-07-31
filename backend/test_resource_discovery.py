#!/usr/bin/env python3
"""
Test script to verify OCI resource discovery functionality.
This will test all resource types and identify specific issues.
"""

import asyncio
import sys
import os
import logging

# Add the backend app to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.cloud_service import OCIService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_oci_clients():
    """Test OCI client initialization and availability"""
    print("=" * 60)
    print("🔍 TESTING OCI CLIENT INITIALIZATION")
    print("=" * 60)
    
    oci_service = OCIService()
    
    print(f"OCI Available: {oci_service.oci_available}")
    print(f"Config: {oci_service.config}")
    print(f"Clients initialized: {list(oci_service.clients.keys())}")
    
    # Test required clients for each resource type
    required_clients = {
        'compartments': 'identity',
        'compute': 'compute', 
        'databases': 'database',
        'oke_clusters': 'container_engine',
        'api_gateways': 'api_gateway',
        'load_balancers': 'load_balancer',
        'network_resources': 'virtual_network',
        'block_volumes': 'block_storage',
        'file_systems': 'file_storage'
    }
    
    missing_clients = []
    for resource_type, client_name in required_clients.items():
        if client_name not in oci_service.clients:
            missing_clients.append(f"{resource_type} -> {client_name}")
            print(f"❌ Missing client for {resource_type}: {client_name}")
        else:
            print(f"✅ Client available for {resource_type}: {client_name}")
    
    if missing_clients:
        print(f"\n⚠️  CRITICAL: Missing clients: {missing_clients}")
        return False, oci_service
    
    return True, oci_service

async def test_compartments(oci_service):
    """Test compartment discovery and hierarchy"""
    print("\n" + "=" * 60)
    print("🔍 TESTING COMPARTMENT DISCOVERY")
    print("=" * 60)
    
    try:
        compartments = await oci_service.get_compartments()
        print(f"Found {len(compartments)} compartments")
        
        if not compartments:
            print("❌ No compartments found")
            return False
        
        # Test hierarchy structure
        for comp in compartments:
            print(f"  📁 {comp.get('name', 'Unknown')} (ID: {comp.get('id', 'N/A')})")
            print(f"     Parent: {comp.get('compartment_id', 'Root')}")
            print(f"     State: {comp.get('lifecycle_state', 'Unknown')}")
        
        # Check for hierarchy relationships
        has_hierarchy = any(comp.get('compartment_id') for comp in compartments)
        print(f"\nHierarchy detected: {has_hierarchy}")
        
        return True
        
    except Exception as e:
        print(f"❌ Compartment discovery failed: {e}")
        return False

async def test_resource_discovery(oci_service, compartments):
    """Test discovery of all resource types"""
    print("\n" + "=" * 60)
    print("🔍 TESTING RESOURCE DISCOVERY")
    print("=" * 60)
    
    if not compartments:
        print("❌ No compartments available for testing")
        return False
    
    # Use the first compartment for testing
    test_compartment = compartments[0]
    compartment_id = test_compartment['id']
    compartment_name = test_compartment.get('name', 'Unknown')
    
    print(f"Testing with compartment: {compartment_name} ({compartment_id})")
    
    resource_tests = {
        'compute_instances': oci_service.get_compute_instances,
        'databases': oci_service.get_databases,
        'oke_clusters': oci_service.get_oke_clusters,
        'api_gateways': oci_service.get_api_gateways,
        'load_balancers': oci_service.get_load_balancers,
        'network_resources': oci_service.get_network_resources,
        'block_volumes': oci_service.get_block_volumes,
        'file_systems': oci_service.get_file_systems
    }
    
    results = {}
    
    for resource_type, test_func in resource_tests.items():
        print(f"\n🔬 Testing {resource_type}...")
        try:
            resources = await test_func(compartment_id)
            results[resource_type] = {
                'success': True,
                'count': len(resources),
                'resources': resources
            }
            print(f"✅ {resource_type}: Found {len(resources)} resources")
            
            # Show sample resource data
            if resources:
                sample = resources[0]
                print(f"   Sample: {sample.get('display_name', sample.get('name', 'Unknown'))}")
                print(f"   ID: {sample.get('id', 'N/A')}")
                print(f"   State: {sample.get('lifecycle_state', 'Unknown')}")
            
        except Exception as e:
            results[resource_type] = {
                'success': False,
                'error': str(e),
                'count': 0
            }
            print(f"❌ {resource_type}: Error - {e}")
    
    return results

async def test_all_resources_endpoint(oci_service, compartments):
    """Test the get_all_resources endpoint"""
    print("\n" + "=" * 60)
    print("🔍 TESTING GET_ALL_RESOURCES ENDPOINT")
    print("=" * 60)
    
    if not compartments:
        print("❌ No compartments available for testing")
        return False
    
    test_compartment = compartments[0]
    compartment_id = test_compartment['id']
    
    try:
        all_resources = await oci_service.get_all_resources(compartment_id)
        
        print(f"Total resources: {all_resources.get('total_resources', 0)}")
        print(f"Last updated: {all_resources.get('last_updated', 'Unknown')}")
        
        resources = all_resources.get('resources', {})
        for resource_type, resource_list in resources.items():
            print(f"  {resource_type}: {len(resource_list)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ get_all_resources failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 STARTING COMPREHENSIVE OCI RESOURCE DISCOVERY TEST")
    print("=" * 80)
    
    # Test 1: Client initialization
    clients_ok, oci_service = await test_oci_clients()
    if not clients_ok:
        print("\n❌ CRITICAL: OCI client initialization failed")
        return False
    
    # Test 2: Compartment discovery
    compartments = await oci_service.get_compartments()
    compartments_ok = await test_compartments(oci_service)
    if not compartments_ok:
        print("\n❌ CRITICAL: Compartment discovery failed")
        return False
    
    # Test 3: Individual resource discovery
    resource_results = await test_resource_discovery(oci_service, compartments)
    
    # Test 4: All resources endpoint
    all_resources_ok = await test_all_resources_endpoint(oci_service, compartments)
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    
    print(f"✅ OCI Clients Initialized: {clients_ok}")
    print(f"✅ Compartments Discovery: {compartments_ok}")
    print(f"✅ All Resources Endpoint: {all_resources_ok}")
    
    print("\n📊 Resource Discovery Results:")
    for resource_type, result in resource_results.items():
        status = "✅" if result['success'] else "❌"
        count = result.get('count', 0)
        print(f"  {status} {resource_type}: {count} resources")
        if not result['success']:
            print(f"      Error: {result.get('error', 'Unknown error')}")
    
    # Identify issues
    failed_resources = [rt for rt, r in resource_results.items() if not r['success']]
    if failed_resources:
        print(f"\n⚠️  ISSUES FOUND WITH: {', '.join(failed_resources)}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 