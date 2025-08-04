"""
Direct test of Kubernetes service to isolate blocking issues
"""

import asyncio
import time
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_kubernetes_service():
    """Test the kubernetes service directly"""
    try:
        print("🧪 Testing Kubernetes Service Directly")
        print("=" * 50)
        
        # Import the service
        print("📋 Importing kubernetes service...")
        from app.services.kubernetes_service_working import working_kubernetes_service
        print("✅ Import successful")
        
        # Test health check
        print("\n📋 Testing health check...")
        start_time = time.time()
        
        try:
            health_result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    working_kubernetes_service.health_check
                ),
                timeout=5.0
            )
            elapsed = time.time() - start_time
            print(f"✅ Health check completed in {elapsed:.2f}s: {health_result.get('status')}")
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"❌ Health check timed out after {elapsed:.2f}s")
            return False
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Health check failed after {elapsed:.2f}s: {e}")
            return False
        
        # Test RBAC without cluster
        print("\n📋 Testing RBAC calls without cluster...")
        start_time = time.time()
        
        try:
            # This should return empty list quickly since no cluster is configured
            roles = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: working_kubernetes_service.get_rbac_roles(None)
                ),
                timeout=5.0
            )
            elapsed = time.time() - start_time
            print(f"✅ RBAC roles call completed in {elapsed:.2f}s (should be empty without cluster)")
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"❌ RBAC roles call timed out after {elapsed:.2f}s")
            return False
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"✅ RBAC roles call failed as expected in {elapsed:.2f}s: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

async def test_access_analyzer_service():
    """Test the access analyzer service directly"""
    try:
        print("\n🧪 Testing Access Analyzer Service Directly")
        print("=" * 50)
        
        # Import the service
        print("📋 Importing access analyzer service...")
        from app.services.access_analyzer_service import get_access_analyzer_service
        print("✅ Import successful")
        
        # Get service instance
        print("\n📋 Getting service instance...")
        start_time = time.time()
        access_analyzer_service = get_access_analyzer_service()
        elapsed = time.time() - start_time
        print(f"✅ Service instantiation completed in {elapsed:.2f}s")
        
        # Test health check
        print("\n📋 Testing health check...")
        start_time = time.time()
        
        try:
            health_result = await asyncio.wait_for(
                access_analyzer_service.health_check(),
                timeout=10.0
            )
            elapsed = time.time() - start_time
            print(f"✅ Health check completed in {elapsed:.2f}s: {health_result.get('status')}")
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"❌ Health check timed out after {elapsed:.2f}s")
            return False
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Health check failed after {elapsed:.2f}s: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Access analyzer test failed: {e}")
        return False

async def main():
    print("🔍 Direct Service Testing - Isolating Blocking Issues")
    print("=" * 60)
    
    # Test kubernetes service
    k8s_result = await test_kubernetes_service()
    
    # Test access analyzer service
    access_result = await test_access_analyzer_service()
    
    print(f"\n🎯 Results:")
    print(f"   Kubernetes Service: {'✅' if k8s_result else '❌'}")
    print(f"   Access Analyzer Service: {'✅' if access_result else '❌'}")
    
    if k8s_result and access_result:
        print("\n✅ Services work directly - issue is in API layer")
    else:
        print("\n❌ Services have blocking issues")

if __name__ == "__main__":
    asyncio.run(main()) 