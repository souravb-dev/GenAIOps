#!/usr/bin/env python3
"""
Test script to verify OCI resource discovery in specific compartments.
This will test resources in their appropriate compartments.
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

async def test_resources_in_proper_compartments():
    """Test resources in their proper compartments"""
    print("=" * 80)
    print("🔍 TESTING RESOURCES IN PROPER COMPARTMENTS")
    print("=" * 80)
    
    oci_service = OCIService()
    
    if not oci_service.oci_available:
        print("❌ OCI not available")
        return False
    
    # Get all compartments
    compartments = await oci_service.get_compartments()
    print(f"Found {len(compartments)} compartments:")
    
    # Create compartment mapping
    comp_map = {comp['name']: comp['id'] for comp in compartments}
    for name, comp_id in comp_map.items():
        print(f"  📁 {name}: {comp_id}")
    
    # Test resource discovery in appropriate compartments
    test_scenarios = [
        # Test databases in Database compartment
        {
            'resource_type': 'databases',
            'method': oci_service.get_databases,
            'compartment_names': ['Database', 'brminfra_isg'],  # Try Database first, then parent
            'description': 'Database resources'
        },
        # Test storage in Storage compartment
        {
            'resource_type': 'block_volumes', 
            'method': oci_service.get_block_volumes,
            'compartment_names': ['Storage', 'brminfra_isg'],
            'description': 'Block volume resources'
        },
        {
            'resource_type': 'file_systems',
            'method': oci_service.get_file_systems,
            'compartment_names': ['Storage', 'brminfra_isg'],
            'description': 'File system resources'
        },
        # Test networking in network compartment
        {
            'resource_type': 'network_resources',
            'method': oci_service.get_network_resources,
            'compartment_names': ['network', 'brminfra_isg'],
            'description': 'Network resources'
        },
        # Test compute in Application compartment
        {
            'resource_type': 'compute_instances',
            'method': oci_service.get_compute_instances, 
            'compartment_names': ['Application', 'brminfra_isg'],
            'description': 'Compute instances'
        },
        # Test OKE in Application compartment
        {
            'resource_type': 'oke_clusters',
            'method': oci_service.get_oke_clusters,
            'compartment_names': ['Application', 'brminfra_isg'],
            'description': 'OKE clusters'
        },
        # Test API Gateways in Application compartment
        {
            'resource_type': 'api_gateways',
            'method': oci_service.get_api_gateways,
            'compartment_names': ['Application', 'brminfra_isg'],
            'description': 'API Gateways'
        },
        # Test Load Balancers in Application compartment
        {
            'resource_type': 'load_balancers',
            'method': oci_service.get_load_balancers,
            'compartment_names': ['Application', 'brminfra_isg'],
            'description': 'Load Balancers'
        }
    ]
    
    results = {}
    
    for scenario in test_scenarios:
        resource_type = scenario['resource_type']
        method = scenario['method']
        compartment_names = scenario['compartment_names']
        description = scenario['description']
        
        print(f"\n🔬 Testing {description} ({resource_type})...")
        
        success = False
        total_resources = 0
        
        for comp_name in compartment_names:
            if comp_name not in comp_map:
                print(f"   ⚠️  Compartment '{comp_name}' not found")
                continue
                
            comp_id = comp_map[comp_name]
            print(f"   🔍 Checking compartment '{comp_name}' ({comp_id[:50]}...)")
            
            try:
                resources = await method(comp_id)
                resource_count = len(resources)
                total_resources += resource_count
                
                if resource_count > 0:
                    print(f"   ✅ Found {resource_count} resources in '{comp_name}'")
                    success = True
                    
                    # Show sample resource
                    sample = resources[0]
                    print(f"      Sample: {sample.get('display_name', sample.get('name', 'Unknown'))}")
                    print(f"      State: {sample.get('lifecycle_state', 'Unknown')}")
                else:
                    print(f"   📭 No resources found in '{comp_name}'")
                    
            except Exception as e:
                error_msg = str(e)
                if "Authorization failed" in error_msg or "Forbidden" in error_msg:
                    print(f"   🚫 Permission denied for '{comp_name}': {error_msg[:100]}...")
                elif "NotAuthorizedOrNotFound" in error_msg:
                    print(f"   🚫 Not authorized or not found in '{comp_name}': {error_msg[:100]}...")
                else:
                    print(f"   ❌ Error in '{comp_name}': {error_msg[:100]}...")
        
        results[resource_type] = {
            'success': success,
            'total_resources': total_resources,
            'description': description
        }
        
        if success:
            print(f"   🎉 {description}: {total_resources} total resources found")
        else:
            print(f"   💔 {description}: No resources found in any compartment")
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 COMPARTMENT-SPECIFIC TEST SUMMARY")
    print("=" * 80)
    
    successful_resources = []
    failed_resources = []
    
    for resource_type, result in results.items():
        if result['success']:
            successful_resources.append(f"{result['description']} ({result['total_resources']})")
            print(f"✅ {result['description']}: {result['total_resources']} resources")
        else:
            failed_resources.append(result['description'])
            print(f"❌ {result['description']}: No resources found")
    
    if successful_resources:
        print(f"\n🎉 SUCCESS: Found resources for {len(successful_resources)} resource types")
        print("   " + "\n   ".join(successful_resources))
    
    if failed_resources:
        print(f"\n⚠️  ISSUES: No resources found for {len(failed_resources)} resource types")
        print("   " + "\n   ".join(failed_resources))
        print("\n💡 This might be due to:")
        print("   - No resources of that type exist in your tenancy")
        print("   - Insufficient permissions to access those compartments")
        print("   - Resources are in different compartments than expected")
    
    return len(successful_resources) > 0

if __name__ == "__main__":
    success = asyncio.run(test_resources_in_proper_compartments())
    sys.exit(0 if success else 1) 