#!/usr/bin/env python3
"""Test the fixed compartments method"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.cloud_service import oci_service

async def test_fixed_compartments():
    try:
        print("🔍 Testing fixed compartments method...")
        compartments = await oci_service.get_compartments()
        print(f"✅ Found {len(compartments)} compartments:")
        for comp in compartments:
            print(f"  - {comp['name']} ({comp['id'][:25]}...)")
        return compartments
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    compartments = asyncio.run(test_fixed_compartments()) 