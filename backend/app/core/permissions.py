from typing import List, Callable
from functools import wraps
from fastapi import HTTPException, status, Depends
from app.services.auth_service import AuthService
from app.models.user import User, RoleEnum

class PermissionChecker:
    """Permission checker class for role-based access control"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    def __call__(self, 
                 current_user: User = Depends(AuthService.get_current_user)) -> User:
        """Check if user has required permissions"""
        # Note: We simplified this to not expose Session in the function signature
        # Permission checking can be done based on user roles directly
        
        # Check if user has required role permissions  
        # Get user roles from database relationship
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            from app.models.user import UserRole, Role
            user_roles_records = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
            user_roles = []
            for user_role in user_roles_records:
                role = db.query(Role).filter(Role.id == user_role.role_id).first()
                if role:
                    user_roles.append(role.name.value)
        finally:
            db.close()
        
        # Map permissions to roles
        permission_role_map = {
            "viewer": ["viewer", "operator", "admin"],
            "operator": ["operator", "admin"], 
            "admin": ["admin"]
        }
        
        for permission in self.required_permissions:
            allowed_roles = permission_role_map.get(permission, [])
            if not any(role in user_roles for role in allowed_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission}"
                )
        
        return current_user

class RoleChecker:
    """Role checker class for role-based access control"""
    
    def __init__(self, required_roles: List[RoleEnum]):
        self.required_roles = required_roles
    
    def __call__(self, 
                 current_user: User = Depends(AuthService.get_current_user)) -> User:
        """Check if user has required roles"""
        # Simplified role checking using the current_user.role field
        if current_user.role not in self.required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role privileges. Required one of: {[role.value for role in self.required_roles]}"
            )
        
        return current_user

# Permission decorators for common access patterns
def require_permissions(*permissions: str):
    """Decorator to require specific permissions"""
    return PermissionChecker(list(permissions))

def require_roles(*roles: RoleEnum):
    """Decorator to require specific roles"""
    return RoleChecker(list(roles))

# Common permission requirements
RequireAdminRole = RoleChecker([RoleEnum.ADMIN])
RequireOperatorRole = RoleChecker([RoleEnum.ADMIN, RoleEnum.OPERATOR])
RequireAnyRole = RoleChecker([RoleEnum.ADMIN, RoleEnum.OPERATOR, RoleEnum.VIEWER])

# Permission-based requirements
RequireDashboardAccess = PermissionChecker(["can_view_dashboard"])
RequireAlertsAccess = PermissionChecker(["can_view_alerts"])
RequireRemediationApproval = PermissionChecker(["can_approve_remediation"])
RequireRemediationExecution = PermissionChecker(["can_execute_remediation"])
RequireUserManagement = PermissionChecker(["can_manage_users"])
RequireRoleManagement = PermissionChecker(["can_manage_roles"])
RequireAccessAnalyzer = PermissionChecker(["can_view_access_analyzer"])
RequirePodAnalyzer = PermissionChecker(["can_view_pod_analyzer"])
RequireCostAnalyzer = PermissionChecker(["can_view_cost_analyzer"])
RequireChatbotAccess = PermissionChecker(["can_use_chatbot"])

# Helper functions simplified to not require database session
def require_permissions(*permissions: str):
    """Decorator to require specific permissions - returns a FastAPI dependency"""
    return PermissionChecker(list(permissions))

def check_user_permissions(user: User, **permissions):
    """Check if user has required permissions (direct function call)"""
    import time
    check_start = time.time()
    
    # For now, just check if user has admin role for all permissions
    # This can be expanded later with more granular permission checking
    print(f"🔍 Permission Debug - User: {user.username}, Checking: {permissions}")
    
    from app.core.database import SessionLocal
    db_start = time.time()
    db = SessionLocal()
    print(f"🔍 Database connection took: {time.time() - db_start:.3f}s")
    
    try:
        query_start = time.time()
        from app.models.user import UserRole, Role
        user_roles_records = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        print(f"🔍 UserRole query took: {time.time() - query_start:.3f}s")
        
        user_roles = []
        role_query_start = time.time()
        for user_role in user_roles_records:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                user_roles.append(role.name.value)
        print(f"🔍 Role queries took: {time.time() - role_query_start:.3f}s")
        print(f"🔍 User roles found: {user_roles}")
    finally:
        db_close_start = time.time()
        db.close()
        print(f"🔍 Database close took: {time.time() - db_close_start:.3f}s")
    
    # Check for admin role - admins can do everything
    if RoleEnum.ADMIN.value in user_roles:
        print(f"✅ Admin role found - allowing all permissions")
        total_time = time.time() - check_start
        print(f"🔍 Total permission check took: {total_time:.3f}s")
        return
    
    print(f"🔍 No admin role, checking specific permissions...")
    
    # For now, require admin for role management permissions
    if permissions.get('can_manage_roles'):
        print(f"❌ Role management requires admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for role management"
        )
    
    # Add other permission checks as needed
    if permissions.get('can_view_access_analyzer'):
        print(f"🔍 Checking access analyzer permission...")
        if not any(role in [RoleEnum.ADMIN.value, RoleEnum.OPERATOR.value] for role in user_roles):
            print(f"❌ Access analyzer requires admin or operator, user has: {user_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin or Operator role required for access analyzer"
            )
        print(f"✅ Access analyzer permission granted")
    
    total_time = time.time() - check_start
    print(f"🔍 Total permission check took: {total_time:.3f}s")
    print(f"✅ All permission checks passed") 