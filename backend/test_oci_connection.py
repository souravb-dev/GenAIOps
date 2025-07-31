#!/usr/bin/env python3
"""
Test OCI connection and configuration
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Test imports
try:
    from app.services.cloud_service import OCIService
    from app.core.config import settings
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_oci_connection():
    """Test OCI connection"""
    print("\n🔧 Testing OCI Configuration...")
    print(f"📁 Config file: {settings.OCI_CONFIG_FILE}")
    print(f"👤 Profile: {settings.OCI_PROFILE}")
    print(f"🌍 Region: {settings.OCI_REGION}")
    
    # Check if config file exists
    if os.path.exists(settings.OCI_CONFIG_FILE):
        print(f"✅ OCI config file found")
    else:
        print(f"❌ OCI config file not found at {settings.OCI_CONFIG_FILE}")
    
    print("\n🔌 Initializing OCI Service...")
    try:
        oci_service = OCIService()
        print(f"✅ OCI Service initialized")
        print(f"🔌 OCI Available: {oci_service.oci_available}")
        
        print("\n📦 Testing compartments...")
        compartments = await oci_service.get_compartments()
        print(f"✅ Retrieved {len(compartments)} compartments:")
        
        for comp in compartments:
            print(f"  - {comp['name']} ({comp['id'][:20]}...)")
        
        return True
        
    except Exception as e:
        print(f"❌ OCI Service error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_oci_connection())
    if success:
        print("\n🎉 OCI connection test successful!")
    else:
        print("\n💔 OCI connection test failed!")
        sys.exit(1) 