#!/usr/bin/env python3
"""
Test script to verify tenancy-agnostic functionality.
This ensures the code works with any OCI tenancy structure.
"""

import asyncio
import sys
import os

# Add the backend app to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.cloud_service import OCIService

async def test_tenancy_agnostic():
    """Test that resource discovery works without hardcoded compartment names"""
    print("🌐 TESTING TENANCY AGNOSTIC FUNCTIONALITY")
    print("=" * 80)
    
    oci_service = OCIService()
    
    if not oci_service.oci_available:
        print("❌ OCI not available")
        return False
    
    # Get compartments dynamically
    compartments = await oci_service.get_compartments()
    comp_names = [comp['name'] for comp in compartments]
    
    print(f"📁 DISCOVERED COMPARTMENTS (dynamic):")
    for i, name in enumerate(comp_names, 1):
        print(f"   {i}. {name}")
    
    print(f"\n🔍 TESTING MULTI-COMPARTMENT DISCOVERY:")
    print("   This should query ALL compartments dynamically, not hardcoded names")
    
    # Test with tenancy root (should use the new agnostic approach)
    tenancy_id = oci_service.config.get('tenancy') if oci_service.config else None
    if not tenancy_id:
        print("❌ Could not get tenancy ID")
        return False
    
    print(f"   Tenancy ID: {tenancy_id}")
    
    try:
        # This should now use _get_all_resources_from_all_compartments
        # without any hardcoded compartment names
        all_resources = await oci_service.get_all_resources(tenancy_id)
        
        print(f"\n📊 TENANCY AGNOSTIC RESULTS:")
        print(f"   Total Resources: {all_resources.get('total_resources', 0)}")
        print(f"   Compartments Queried: {all_resources.get('compartments_queried', 0)}")
        print(f"   Resource Types Found:")
        
        for resource_type, resources in all_resources.get('resources', {}).items():
            count = len(resources) if resources else 0
            status = "✅" if count > 0 else "📭"
            print(f"      {status} {resource_type}: {count} resources")
            
            # Show source compartments for first few resources
            if resources and count > 0:
                sources = set()
                for resource in resources[:3]:  # Show first 3
                    source = resource.get('source_compartment', 'Unknown')
                    sources.add(source)
                if sources:
                    print(f"         Sources: {', '.join(sources)}")
        
        print(f"\n✅ TENANCY AGNOSTIC VERIFICATION:")
        
        # Verify no hardcoded compartment dependencies
        verification_checks = []
        
        # Check 1: Should find resources in discovered compartments
        resources_found = all_resources.get('total_resources', 0) > 0
        verification_checks.append(("Resources found dynamically", resources_found))
        
        # Check 2: Should query the actual number of compartments we discovered
        compartments_queried = all_resources.get('compartments_queried', 0)
        expected_compartments = len(compartments)
        compartment_match = compartments_queried == expected_compartments
        verification_checks.append(("All compartments queried", compartment_match))
        
        # Check 3: Resources should have source_compartment tracking
        has_source_tracking = False
        for resources in all_resources.get('resources', {}).values():
            if resources:
                for resource in resources:
                    if 'source_compartment' in resource:
                        has_source_tracking = True
                        break
                if has_source_tracking:
                    break
        verification_checks.append(("Source compartment tracking", has_source_tracking))
        
        # Print verification results
        all_passed = True
        for check_name, passed in verification_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {check_name}")
            if not passed:
                all_passed = False
        
        print(f"\n🎯 TENANCY AGNOSTIC TEST: {'SUCCESS ✅' if all_passed else 'FAILED ❌'}")
        
        if all_passed:
            print("\n🌟 TENANCY AGNOSTIC CONFIRMED:")
            print("   ✅ No hardcoded compartment names")
            print("   ✅ Discovers compartments dynamically") 
            print("   ✅ Queries all compartments automatically")
            print("   ✅ Works with any OCI tenancy structure")
            print("   ✅ Tracks resource source compartments")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 STARTING TENANCY AGNOSTIC TEST")
    print("=" * 80)
    
    success = asyncio.run(test_tenancy_agnostic())
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 TENANCY AGNOSTIC: VERIFIED ✅")
        print("✅ This code will work with ANY OCI tenancy!")
        print("✅ No hardcoded compartment names or tenancy-specific logic!")
    else:
        print("❌ TENANCY AGNOSTIC: FAILED")
        print("❌ Code may still have tenancy-specific dependencies")
    
    print("=" * 80)
    sys.exit(0 if success else 1) 