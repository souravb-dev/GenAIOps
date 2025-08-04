"""
Timing Debug Script - Isolate the 2-second delay
"""
import time
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_timing(description, func):
    """Test timing of a function"""
    print(f"\n🔍 Testing: {description}")
    start_time = time.time()
    try:
        result = func()
        elapsed = time.time() - start_time
        print(f"✅ Success in {elapsed:.3f}s")
        return result, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error in {elapsed:.3f}s: {e}")
        return None, elapsed

def test_database_connection():
    """Test database connection"""
    from app.core.database import SessionLocal
    db = SessionLocal()
    db.close()
    return "DB connection OK"

def test_user_query():
    """Test user database query"""
    from app.core.database import SessionLocal
    from app.models.user import User, UserRole, Role
    
    db = SessionLocal()
    try:
        # Query admin user
        admin_user = db.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            return "Admin user not found"
        
        # Query user roles
        user_roles_records = db.query(UserRole).filter(UserRole.user_id == admin_user.id).all()
        
        # Query roles
        user_roles = []
        for user_role in user_roles_records:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                user_roles.append(role.name.value)
        
        return f"User {admin_user.username} has roles: {user_roles}"
    finally:
        db.close()

def test_access_analyzer_import():
    """Test importing AccessAnalyzerService"""
    from app.services.access_analyzer_service import AccessAnalyzerService
    return "AccessAnalyzerService imported"

def test_access_analyzer_creation():
    """Test creating AccessAnalyzerService"""
    from app.services.access_analyzer_service import get_access_analyzer_service
    service = get_access_analyzer_service()
    return f"AccessAnalyzerService created: {type(service)}"

def test_kubernetes_service_import():
    """Test importing Kubernetes service"""
    from app.services.kubernetes_service_working import WorkingKubernetesService
    return "WorkingKubernetesService imported"

def test_kubernetes_service_creation():
    """Test creating Kubernetes service"""
    from app.services.kubernetes_service_working import WorkingKubernetesService
    service = WorkingKubernetesService()
    return f"WorkingKubernetesService created, configured: {service.is_configured}"

def test_lazy_kubernetes_access():
    """Test accessing Kubernetes service via lazy property"""
    from app.services.access_analyzer_service import get_access_analyzer_service
    service = get_access_analyzer_service()
    k8s_service = service.kubernetes_service  # This should trigger lazy loading
    return f"Kubernetes service lazy loaded, configured: {k8s_service.is_configured}"

if __name__ == "__main__":
    print("🧪 TIMING DEBUG - Isolating 2-second delay")
    print("=" * 50)
    
    # Test individual components
    tests = [
        ("Database Connection", test_database_connection),
        ("User Query", test_user_query),
        ("AccessAnalyzer Import", test_access_analyzer_import),
        ("AccessAnalyzer Creation", test_access_analyzer_creation),
        ("Kubernetes Import", test_kubernetes_service_import),
        ("Kubernetes Creation", test_kubernetes_service_creation),
        ("Lazy Kubernetes Access", test_lazy_kubernetes_access),
    ]
    
    total_time = 0
    for description, func in tests:
        result, elapsed = test_timing(description, func)
        total_time += elapsed
        
        # If any test takes >1 second, highlight it
        if elapsed > 1.0:
            print(f"🚨 SLOW OPERATION FOUND: {description} took {elapsed:.3f}s")
    
    print(f"\n🎯 TOTAL TIME: {total_time:.3f}s")
    print("\n🔍 Analysis:")
    print("- Operations >1s are likely causing the delay")
    print("- Focus on the slowest operations first") 