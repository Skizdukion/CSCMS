from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based permissions.
    Extends Django's AbstractUser to add role-based access control.
    """
    
    class Role(models.TextChoices):
        GUEST = 'guest', _('Guest')
        ADMINISTRATOR = 'administrator', _('Administrator')
        BRAND_MANAGER = 'brand_manager', _('Brand Manager')
        STORE_MANAGER = 'store_manager', _('Store Manager')
    
    # Role field
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST,
        help_text=_('User role determines access permissions')
    )
    
    # Profile fields
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_('Contact phone number')
    )
    
    # Additional profile information
    address = models.TextField(
        blank=True,
        null=True,
        help_text=_('User address')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Meta options
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_administrator(self):
        """Check if user is an administrator."""
        return self.role == self.Role.ADMINISTRATOR
    
    @property
    def is_brand_manager(self):
        """Check if user is a brand manager."""
        return self.role == self.Role.BRAND_MANAGER
    
    @property
    def is_store_manager(self):
        """Check if user is a store manager."""
        return self.role == self.Role.STORE_MANAGER
    
    @property
    def is_guest(self):
        """Check if user is a guest."""
        return self.role == self.Role.GUEST
    
    def has_permission(self, permission_name):
        """
        Check if user has a specific permission based on their role.
        
        Args:
            permission_name (str): Name of the permission to check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Administrator has all permissions
        if self.is_administrator:
            return True
        
        # Define role-based permissions
        role_permissions = {
            self.Role.BRAND_MANAGER: [
                'view_store',
                'view_brand_inventory',
                'manage_brand_inventory',
                'view_reviews',
                'create_review',
                'update_review',
                'delete_own_review',
            ],
            self.Role.STORE_MANAGER: [
                'view_store',
                'manage_store_inventory',
                'view_reviews',
                'create_review',
                'update_review',
                'delete_own_review',
            ],
            self.Role.GUEST: [
                'view_store',
                'view_reviews',
                'create_review',
                'update_own_review',
                'delete_own_review',
            ],
        }
        
        return permission_name in role_permissions.get(self.role, [])
    
    def can_manage_user(self, target_user):
        """
        Check if this user can manage another user.
        
        Args:
            target_user (User): The user to check management permissions for
            
        Returns:
            bool: True if user can manage target_user, False otherwise
        """
        # Administrators can manage all users
        if self.is_administrator:
            return True
        
        # Users cannot manage themselves
        if self == target_user:
            return False
        
        # Brand managers can manage store managers and guests
        if self.is_brand_manager:
            return target_user.role in [self.Role.STORE_MANAGER, self.Role.GUEST]
        
        # Store managers can manage guests
        if self.is_store_manager:
            return target_user.role == self.Role.GUEST
        
        # Guests cannot manage anyone
        return False
