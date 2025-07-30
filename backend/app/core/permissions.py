from typing import List, Callable
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User, RoleEnum

class PermissionChecker:
    """Permission checker class for role-based access control"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    def __call__(self, 
                 current_user: User = Depends(AuthService.get_current_user),
                 db: Session = Depends(get_db)) -> User:
        """Check if user has required permissions"""
        user_permissions = AuthService.get_user_permissions(db, current_user)
        
        # Check if user has all required permissions
        for permission in self.required_permissions:
            if not user_permissions.get(permission, False):
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
                 current_user: User = Depends(AuthService.get_current_user),
                 db: Session = Depends(get_db)) -> User:
        """Check if user has required roles"""
        from app.models.user import UserRole
        
        user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
        user_role_names = []
        
        for user_role in user_roles:
            role = db.query(User).filter(User.id == user_role.role_id).first()
            if role:
                user_role_names.append(role.name)
        
        # Check if user has any of the required roles
        has_required_role = any(role in user_role_names for role in self.required_roles)
        
        if not has_required_role:
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

def check_user_permission(user: User, db: Session, permission: str) -> bool:
    """Helper function to check if user has specific permission"""
    permissions = AuthService.get_user_permissions(db, user)
    return permissions.get(permission, False)

def check_user_role(user: User, db: Session, role: RoleEnum) -> bool:
    """Helper function to check if user has specific role"""
    from app.models.user import UserRole, Role
    
    user_roles = db.query(UserRole)\
        .join(Role, UserRole.role_id == Role.id)\
        .filter(UserRole.user_id == user.id, Role.name == role)\
        .first()
    
    return user_roles is not None

def get_user_roles(user: User, db: Session) -> List[RoleEnum]:
    """Get all roles for a user"""
    from app.models.user import UserRole, Role
    
    user_roles = db.query(Role)\
        .join(UserRole, Role.id == UserRole.role_id)\
        .filter(UserRole.user_id == user.id)\
        .all()
    
    return [role.name for role in user_roles] 