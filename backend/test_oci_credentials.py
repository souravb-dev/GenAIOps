#!/usr/bin/env python3
"""
Test OCI credentials and connection
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_oci_files():
    """Test if OCI config and key files exist"""
    print("🔍 Testing OCI Files:")
    
    config_file = "C:\\Users\\2374439\\.oci\\config"
    key_file = "C:\\Users\\2374439\\.oci\\oci_api_key.pem"
    
    print(f"  Config file: {config_file}")
    if os.path.exists(config_file):
        print("  ✅ Config file exists")
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                if 'eu-frankfurt-1' in content:
                    print("  ✅ Correct region (eu-frankfurt-1) found in config")
                else:
                    print("  ⚠️  Region check - looking for eu-frankfurt-1...")
        except Exception as e:
            print(f"  ❌ Error reading config: {e}")
    else:
        print("  ❌ Config file not found")
    
    print(f"  Key file: {key_file}")
    if os.path.exists(key_file):
        print("  ✅ Key file exists")
        # Check key file permissions (should be readable)
        try:
            with open(key_file, 'r') as f:
                key_content = f.read()
                if 'BEGIN RSA PRIVATE KEY' in key_content or 'BEGIN PRIVATE KEY' in key_content:
                    print("  ✅ Key file appears to be valid")
                else:
                    print("  ⚠️  Key file format may be incorrect")
        except Exception as e:
            print(f"  ❌ Error reading key file: {e}")
    else:
        print("  ❌ Key file not found")

def test_oci_import():
    """Test OCI SDK import and basic functionality"""
    print("\n🔍 Testing OCI SDK:")
    
    try:
        import oci
        print(f"  ✅ OCI SDK imported successfully (version: {oci.__version__})")
        
        # Test configuration loading
        try:
            config = oci.config.from_file("C:\\Users\\2374439\\.oci\\config", "DEFAULT")
            print("  ✅ OCI config loaded successfully")
            
            # Test config validation
            try:
                oci.config.validate_config(config)
                print("  ✅ OCI config validation passed")
                print(f"    - Region: {config.get('region')}")
                print(f"    - User ID: {config.get('user', 'N/A')[:20]}...")
                print(f"    - Tenancy ID: {config.get('tenancy', 'N/A')[:20]}...")
                return config
            except Exception as e:
                print(f"  ❌ Config validation failed: {e}")
                return None
                
        except Exception as e:
            print(f"  ❌ Config loading failed: {e}")
            return None
            
    except ImportError as e:
        print(f"  ❌ OCI SDK import failed: {e}")
        return None

async def test_oci_connection(config):
    """Test actual OCI API connection"""
    if not config:
        print("\n❌ Skipping connection test - no valid config")
        return False
        
    print("\n🔍 Testing OCI API Connection:")
    
    try:
        import oci
        # Test identity service connection
        identity_client = oci.identity.IdentityClient(config)
        
        # Simple API call to get tenancy information
        tenancy_id = config['tenancy']
        response = identity_client.get_tenancy(tenancy_id)
        
        print(f"  ✅ Successfully connected to OCI!")
        print(f"    - Tenancy Name: {response.data.name}")
        print(f"    - Home Region: {response.data.home_region_key}")
        print(f"    - Description: {response.data.description}")
        
        return True
        
    except oci.exceptions.ServiceError as e:
        print(f"  ❌ OCI API error: {e.message}")
        print(f"    - Status: {e.status}")
        print(f"    - Code: {e.code}")
        return False
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        return False

async def test_compartments(config):
    """Test compartment listing"""
    if not config:
        return False
        
    print("\n🔍 Testing Compartment Access:")
    
    try:
        import oci
        identity_client = oci.identity.IdentityClient(config)
        tenancy_id = config['tenancy']
        
        # List compartments
        response = identity_client.list_compartments(
            tenancy_id,
            compartment_id_in_subtree=True
        )
        
        print(f"  ✅ Found {len(response.data)} compartments")
        for i, comp in enumerate(response.data[:3]):  # Show first 3
            print(f"    {i+1}. {comp.name} ({comp.lifecycle_state})")
        
        if len(response.data) > 3:
            print(f"    ... and {len(response.data) - 3} more")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Compartment listing failed: {e}")
        return False

async def main():
    """Run all OCI tests"""
    print("🧪 OCI Credentials and Connection Test")
    print("=" * 50)
    
    # Test 1: File existence
    test_oci_files()
    
    # Test 2: OCI SDK and config
    config = test_oci_import()
    
    # Test 3: API connection
    connection_success = await test_oci_connection(config)
    
    # Test 4: Compartment access
    if connection_success:
        await test_compartments(config)
    
    print("\n" + "=" * 50)
    if connection_success:
        print("✅ OCI Connection Test PASSED!")
        print("Your backend should now connect to real OCI data.")
        print("Restart your backend service to see live data.")
    else:
        print("❌ OCI Connection Test FAILED!")
        print("Please check your credentials and network connectivity.")

if __name__ == "__main__":
    asyncio.run(main()) 