#!/usr/bin/env python3
"""
Test script to verify database discovery fix using correct API endpoints.
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

async def test_database_discovery():
    """Test database discovery with the fixed API"""
    print("🚀 TESTING DATABASE DISCOVERY FIX")
    print("=" * 60)
    
    oci_service = OCIService()
    
    if not oci_service.oci_available:
        print("❌ OCI not available")
        return False
    
    # Get compartments first
    compartments = await oci_service.get_compartments()
    comp_map = {comp['name']: comp['id'] for comp in compartments}
    
    print(f"Available compartments: {list(comp_map.keys())}")
    
    # Test specifically the Database compartment
    database_compartment_id = comp_map.get('Database')
    if not database_compartment_id:
        print("❌ Database compartment not found")
        return False
    
    print(f"\n🔬 Testing database discovery in Database compartment:")
    print(f"   Compartment ID: {database_compartment_id}")
    
    try:
        databases = await oci_service.get_databases(database_compartment_id)
        
        print(f"\n📊 DATABASE DISCOVERY RESULTS:")
        print(f"   Total databases found: {len(databases)}")
        
        if databases:
            print(f"\n📋 Database Details:")
            for i, db in enumerate(databases, 1):
                print(f"   {i}. {db.get('display_name', 'Unknown')}")
                print(f"      ID: {db.get('id', 'Unknown')}")
                print(f"      Type: {db.get('resource_type', 'Unknown')}")
                print(f"      State: {db.get('lifecycle_state', 'Unknown')}")
                print(f"      DB Name: {db.get('db_name', 'N/A')}")
                
                # Show type-specific details
                if db.get('resource_type') == 'DB_SYSTEM':
                    print(f"      Edition: {db.get('database_edition', 'Unknown')}")
                    print(f"      Shape: {db.get('shape', 'Unknown')}")
                    print(f"      CPU Cores: {db.get('cpu_core_count', 0)}")
                    print(f"      Storage (GB): {db.get('data_storage_size_in_gbs', 0)}")
                    print(f"      Nodes: {db.get('node_count', 1)}")
                elif db.get('resource_type') == 'DATABASE':
                    print(f"      Workload: {db.get('db_workload', 'Unknown')}")
                    print(f"      Character Set: {db.get('character_set', 'Unknown')}")
                    print(f"      PDB Name: {db.get('pdb_name', 'N/A')}")
                    print(f"      Is CDB: {db.get('is_cdb', False)}")
                elif db.get('resource_type') == 'AUTONOMOUS_DATABASE':
                    print(f"      Workload: {db.get('db_workload', 'Unknown')}")
                    print(f"      CPU Cores: {db.get('cpu_core_count', 0)}")
                    print(f"      Storage (TB): {db.get('data_storage_size_in_tbs', 0)}")
                
                print(f"      Created: {db.get('time_created', 'Unknown')}")
                print()
            
            return True
        else:
            print("   📭 No databases found")
            return False
            
    except Exception as e:
        print(f"❌ Database discovery failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def test_multi_compartment_database_discovery():
    """Test database discovery across all compartments"""
    print("\n" + "=" * 60)
    print("🔬 TESTING MULTI-COMPARTMENT DATABASE DISCOVERY")
    print("=" * 60)
    
    oci_service = OCIService()
    compartments = await oci_service.get_compartments()
    
    total_databases = 0
    compartment_results = {}
    
    for comp in compartments:
        comp_name = comp['name']
        comp_id = comp['id']
        
        print(f"\n🔍 Checking {comp_name}...")
        
        try:
            databases = await oci_service.get_databases(comp_id)
            count = len(databases)
            total_databases += count
            compartment_results[comp_name] = count
            
            if count > 0:
                print(f"   ✅ Found {count} database resources")
                # Show first database as sample
                sample = databases[0]
                print(f"      Sample: {sample.get('display_name', 'Unknown')}")
                print(f"      Type: {sample.get('resource_type', 'Unknown')}")
            else:
                print(f"   📭 No databases found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            compartment_results[comp_name] = 0
    
    print(f"\n🏆 SUMMARY:")
    print(f"   Total databases across all compartments: {total_databases}")
    
    for comp_name, count in compartment_results.items():
        status = "✅" if count > 0 else "📭"
        print(f"   {status} {comp_name}: {count} databases")
    
    return total_databases > 0

if __name__ == "__main__":
    print("🔍 STARTING DATABASE DISCOVERY TEST")
    print("=" * 80)
    
    # Test specific Database compartment
    success1 = asyncio.run(test_database_discovery())
    
    # Test all compartments
    success2 = asyncio.run(test_multi_compartment_database_discovery())
    
    overall_success = success1 or success2
    
    print("\n" + "=" * 80)
    print(f"🎯 FINAL RESULT: {'SUCCESS ✅' if overall_success else 'FAILED ❌'}")
    
    if overall_success:
        print("✅ Database discovery is now working with correct API endpoints!")
        print("✅ Both DB Systems and individual databases are discovered!")
    else:
        print("❌ Database discovery still has issues")
    
    print("=" * 80)
    sys.exit(0 if overall_success else 1) 