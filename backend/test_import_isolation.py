"""
Import Isolation Test - Find the 54-second culprit
"""
import time
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import(description, import_func):
    """Test timing of an import"""
    print(f"\n🔍 Testing Import: {description}")
    start_time = time.time()
    try:
        result = import_func()
        elapsed = time.time() - start_time
        if elapsed > 5.0:
            print(f"🚨 VERY SLOW: {elapsed:.3f}s")
        elif elapsed > 1.0:
            print(f"🚨 SLOW: {elapsed:.3f}s")
        else:
            print(f"✅ Fast: {elapsed:.3f}s")
        return result, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error in {elapsed:.3f}s: {e}")
        return None, elapsed

# Test individual imports from access_analyzer_service.py
def import_kubernetes_types():
    from app.services.kubernetes_service_working import RBACRole, RBACBinding
    return "RBACRole, RBACBinding imported"

def import_genai_types():
    from app.services.genai_service import GenAIRequest
    return "GenAIRequest imported"

def import_exceptions():
    from app.core.exceptions import ExternalServiceError
    return "ExternalServiceError imported"

def import_database():
    from app.core.database import SessionLocal
    return "SessionLocal imported"

def import_user_models():
    from app.models.user import User, UserRole, Role
    return "User models imported"

if __name__ == "__main__":
    print("🧪 IMPORT ISOLATION TEST - Finding 54-second delay")
    print("=" * 60)
    
    # Test individual imports that access_analyzer_service.py uses
    tests = [
        ("Kubernetes Types (RBACRole, RBACBinding)", import_kubernetes_types),
        ("GenAI Types (GenAIRequest)", import_genai_types),
        ("Exceptions", import_exceptions),
        ("Database", import_database),
        ("User Models", import_user_models),
    ]
    
    slow_imports = []
    for description, func in tests:
        result, elapsed = test_import(description, func)
        if elapsed > 5.0:
            slow_imports.append((description, elapsed))
    
    print(f"\n🎯 RESULTS:")
    if slow_imports:
        print("🚨 SLOW IMPORTS FOUND:")
        for desc, elapsed in slow_imports:
            print(f"   - {desc}: {elapsed:.3f}s")
    else:
        print("✅ All imports are fast - issue might be elsewhere")
        
    print("\n🔍 Next step: Focus on the slowest import to find root cause") 