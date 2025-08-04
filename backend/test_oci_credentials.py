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
    
    config_file = "C:\\Users\\2375603\\.oci\\config"
    key_file = "C:\\Users\\2375603\\.oci\\oci_api_key.pem"
    
    print(f"  Config file: {config_file}")
    if os.path.exists(config_file):
        print("  ✅ Config file exists")
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                if 'user' in content and 'tenancy' in content:
                    print("  ✅ Config file contains required fields")
                else:
                    print("  ⚠️  Config file missing required fields")
        except Exception as e:
            print(f"  ❌ Error reading config file: {e}")
    else:
        print("  ❌ Config file not found")
    
    print(f"  Key file: {key_file}")
    if os.path.exists(key_file):
        print("  ✅ Key file exists")
    else:
        print("  ❌ Key file not found")

def test_oci_config_parsing():
    """Test OCI config parsing"""
    print("\n🔧 Testing OCI Config Parsing:")
    
    try:
        # Load configuration
        config = oci.config.from_file()
        print("  ✅ Config loaded successfully using default location")
        
        # Validate required fields
        required_fields = ['user', 'fingerprint', 'tenancy', 'region', 'key_file']
        for field in required_fields:
            if field in config:
                print(f"  ✅ {field}: {config[field][:20]}..." if len(str(config[field])) > 20 else f"  ✅ {field}: {config[field]}")
            else:
                print(f"  ❌ Missing {field}")
                
    except oci.exceptions.ConfigFileNotFound as e:
        print(f"  ❌ Config file not found: {e}")
    except oci.exceptions.InvalidConfig as e:
        print(f"  ❌ Invalid config: {e}")
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")

def test_oci_auth():
    """Test OCI authentication"""
    print("\n🔐 Testing OCI Authentication:")
    
    try:
        # Test config with specific file path
        config = oci.config.from_file("C:\\Users\\2375603\\.oci\\config", "DEFAULT")
        
        # Validate config
        oci.config.validate_config(config)
        print("  ✅ Config validation passed")
        
        # Try to create a simple client
        identity_client = oci.identity.IdentityClient(config)
        print("  ✅ Identity client created successfully")
        
        return True
        
    except oci.exceptions.ConfigFileNotFound as e:
        print(f"  ❌ Config file not found: {e}")
    except oci.exceptions.InvalidConfig as e:
        print(f"  ❌ Invalid config: {e}")
    except oci.exceptions.ServiceError as e:
        print(f"  ❌ Service error: {e}")
    except Exception as e:
        print(f"  ❌ Authentication error: {e}")
    
    return False

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