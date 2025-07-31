#!/usr/bin/env python3
"""
Final comprehensive test to verify all fixes:
1. Compartment hierarchy display
2. Multi-compartment resource discovery  
3. All resource types working
4. End-to-end functionality
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

def display_compartment_hierarchy(compartments):
    """Display compartments in hierarchical format"""
    print("\n📁 COMPARTMENT HIERARCHY:")
    print("=" * 50)
    
    # Build hierarchy mapping
    comp_map = {comp['id']: comp for comp in compartments}
    
    def build_hierarchy(parent_id=None, level=0):
        children = [comp for comp in compartments if comp.get('compartment_id') == parent_id]
        if not children and parent_id is None:
            # Handle case where we need to find root compartments
            children = [comp for comp in compartments if not comp.get('compartment_id') or comp['name'].lower().startswith('root')]
        
        children.sort(key=lambda x: x['name'])
        
        for comp in children:
            indent = "  " * level
            prefix = "├─ " if level > 0 else ""
            status_icon = "✅" if comp['lifecycle_state'] == 'ACTIVE' else "⚠️"
            
            print(f"{indent}{prefix}{status_icon} {comp['name']}")
            print(f"{indent}    ID: {comp['id'][:50]}...")
            print(f"{indent}    State: {comp['lifecycle_state']}")
            
            # Find children
            child_comps = [c for c in compartments if c.get('compartment_id') == comp['id']]
            if child_comps:
                build_hierarchy(comp['id'], level + 1)
    
    build_hierarchy()

async def test_comprehensive_functionality():
    """Test all functionality comprehensively"""
    print("🚀 FINAL COMPREHENSIVE TEST")
    print("=" * 80)
    
    oci_service = OCIService()
    
    if not oci_service.oci_available:
        print("❌ OCI not available")
        return False
    
    print("✅ OCI Connection Established")
    print(f"   Tenancy: {oci_service.config.get('tenancy', 'Unknown')}")
    print(f"   Region: {oci_service.config.get('region', 'Unknown')}")
    print(f"   User: {oci_service.config.get('user', 'Unknown')}")
    
    # Test 1: Compartment Discovery & Hierarchy
    print("\n" + "=" * 80)
    print("🧪 TEST 1: COMPARTMENT DISCOVERY & HIERARCHY")
    print("=" * 80)
    
    compartments = await oci_service.get_compartments()
    print(f"Found {len(compartments)} compartments")
    
    if compartments:
        display_compartment_hierarchy(compartments)
        hierarchy_test = True
    else:
        print("❌ No compartments found")
        hierarchy_test = False
    
    # Test 2: Multi-Compartment Resource Discovery (Tenancy Root)
    print("\n" + "=" * 80)
    print("🧪 TEST 2: MULTI-COMPARTMENT RESOURCE DISCOVERY")
    print("=" * 80)
    
    # Test with tenancy root (should trigger multi-compartment query)
    tenancy_id = oci_service.config.get('tenancy')
    print(f"Testing with tenancy root: {tenancy_id}")
    
    try:
        all_resources = await oci_service.get_all_resources(tenancy_id)
        
        print(f"📊 RESOURCE DISCOVERY RESULTS:")
        print(f"   Total Resources: {all_resources.get('total_resources', 0)}")
        print(f"   Compartments Queried: {all_resources.get('compartments_queried', 0)}")
        print(f"   Last Updated: {all_resources.get('last_updated', 'Unknown')}")
        
        resources = all_resources.get('resources', {})
        resource_summary = {}
        
        for resource_type, resource_list in resources.items():
            count = len(resource_list)
            resource_summary[resource_type] = count
            status = "✅" if count > 0 else "📭"
            print(f"   {status} {resource_type}: {count} resources")
            
            # Show sample resources
            if count > 0:
                sample = resource_list[0]
                print(f"      Sample: {sample.get('display_name', sample.get('name', 'Unknown'))}")
                print(f"      State: {sample.get('lifecycle_state', 'Unknown')}")
        
        multi_compartment_test = all_resources.get('total_resources', 0) > 0
        
    except Exception as e:
        print(f"❌ Multi-compartment resource discovery failed: {e}")
        multi_compartment_test = False
        resource_summary = {}
    
    # Test 3: Individual Compartment Resource Discovery
    print("\n" + "=" * 80)
    print("🧪 TEST 3: INDIVIDUAL COMPARTMENT TESTING")
    print("=" * 80)
    
    individual_tests = {}
    if compartments:
        # Test a few specific compartments
        test_compartments = [
            ('Application', 'compute_instances'),
            ('Storage', 'block_volumes'),
            ('network', 'network_resources')
        ]
        
        comp_map = {comp['name']: comp['id'] for comp in compartments}
        
        for comp_name, expected_resource in test_compartments:
            if comp_name in comp_map:
                comp_id = comp_map[comp_name]
                print(f"\n🔬 Testing {comp_name} compartment:")
                
                try:
                    comp_resources = await oci_service.get_all_resources(comp_id)
                    total = comp_resources.get('total_resources', 0)
                    print(f"   Total resources: {total}")
                    
                    if total > 0:
                        individual_tests[comp_name] = True
                        print(f"   ✅ {comp_name} has resources")
                    else:
                        individual_tests[comp_name] = False
                        print(f"   📭 {comp_name} has no resources")
                        
                except Exception as e:
                    individual_tests[comp_name] = False
                    print(f"   ❌ {comp_name} test failed: {e}")
    
    # Test 4: API Endpoints (simulated)
    print("\n" + "=" * 80)
    print("🧪 TEST 4: API ENDPOINT VERIFICATION")
    print("=" * 80)
    
    endpoint_tests = {
        'get_compartments': True,  # Already tested
        'get_all_resources': multi_compartment_test,
        'resource_discovery': len(resource_summary) > 0
    }
    
    for endpoint, status in endpoint_tests.items():
        print(f"   {'✅' if status else '❌'} {endpoint}")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("🏆 FINAL TEST SUMMARY")
    print("=" * 80)
    
    print(f"✅ Compartment Hierarchy: {'WORKING' if hierarchy_test else 'FAILED'}")
    print(f"✅ Multi-Compartment Discovery: {'WORKING' if multi_compartment_test else 'FAILED'}")
    print(f"✅ Individual Compartment Tests: {sum(individual_tests.values())}/{len(individual_tests)} passed")
    
    print(f"\n📊 Resource Type Summary:")
    working_resources = 0
    total_resource_types = len(resource_summary) if resource_summary else 0
    
    if resource_summary:
        for resource_type, count in resource_summary.items():
            if count > 0:
                working_resources += 1
                print(f"   ✅ {resource_type}: {count} resources")
            else:
                print(f"   📭 {resource_type}: No resources (may be legitimate)")
    
    print(f"\n🎯 OVERALL RESULT:")
    print(f"   Resource Types Working: {working_resources}/{total_resource_types}")
    print(f"   Compartment Hierarchy: {'✅ WORKING' if hierarchy_test else '❌ FAILED'}")
    print(f"   Multi-Compartment Query: {'✅ WORKING' if multi_compartment_test else '❌ FAILED'}")
    
    # Determine overall success
    overall_success = (
        hierarchy_test and 
        multi_compartment_test and 
        working_resources >= 5  # At least 5 resource types working
    )
    
    if overall_success:
        print(f"\n🎉 SUCCESS: All critical functionality is working!")
        print(f"   ✅ Compartment hierarchy implemented")
        print(f"   ✅ Resource discovery fixed")
        print(f"   ✅ Multi-compartment querying working")
        print(f"   ✅ {working_resources} resource types discovered")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: Some issues remain")
        if not hierarchy_test:
            print(f"   ❌ Compartment hierarchy needs work")
        if not multi_compartment_test:
            print(f"   ❌ Multi-compartment discovery needs work")
        if working_resources < 5:
            print(f"   ❌ Only {working_resources} resource types working")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(test_comprehensive_functionality())
    print(f"\n{'='*80}")
    print(f"🎯 FINAL RESULT: {'SUCCESS ✅' if success else 'NEEDS MORE WORK ⚠️'}")
    print(f"{'='*80}")
    sys.exit(0 if success else 1) 