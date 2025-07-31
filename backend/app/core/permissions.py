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