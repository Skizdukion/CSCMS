from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdministrator(permissions.BasePermission):
    """
    Custom permission to only allow administrators.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_administrator


class IsBrandManager(permissions.BasePermission):
    """
    Custom permission to only allow brand managers.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_brand_manager


class IsStoreManager(permissions.BasePermission):
    """
    Custom permission to only allow store managers.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_store_manager


class IsAuthenticatedUser(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


class HasSpecificPermission(permissions.BasePermission):
    """
    Custom permission to check if user has a specific permission.
    """
    
    def __init__(self, permission_name):
        self.permission_name = permission_name
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_permission(self.permission_name)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class CanManageUser(permissions.BasePermission):
    """
    Custom permission to check if user can manage another user.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions are only allowed if user can manage the target user
        return request.user.can_manage_user(obj)


class RoleBasedPermission(permissions.BasePermission):
    """
    Custom permission that allows different actions based on user role.
    """
    
    def __init__(self, allowed_roles=None, admin_override=True):
        self.allowed_roles = allowed_roles or []
        self.admin_override = admin_override
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Administrators can do everything if admin_override is True
        if self.admin_override and request.user.is_administrator:
            return True
        
        # Check if user's role is in allowed roles
        return request.user.role in self.allowed_roles


class IsOwnerOrHasRolePermission(permissions.BasePermission):
    """
    Custom permission that allows owners or users with specific roles to access objects.
    """
    
    def __init__(self, required_roles=None, admin_override=True):
        self.required_roles = required_roles or []
        self.admin_override = admin_override
    
    def has_object_permission(self, request, view, obj):
        # Administrators can do everything if admin_override is True
        if self.admin_override and request.user.is_administrator:
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Check if user has required role
        if request.user.role in self.required_roles:
            return True
        
        return False
