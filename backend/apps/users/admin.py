from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    Extends Django's default UserAdmin with role-based features.
    """
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'role',
        'is_active', 'is_staff', 'date_joined'
    ]
    
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser',
        'date_joined', 'created_at'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name',
        'phone_number', 'address'
    ]
    
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address')
        }),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activate_users', 'deactivate_users', 'make_administrators', 'make_brand_managers', 'make_store_managers']
    
    def activate_users(self, request, queryset):
        """Activate selected users."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} user(s) were successfully activated.'
        )
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} user(s) were successfully deactivated.'
        )
    deactivate_users.short_description = "Deactivate selected users"
    
    def make_administrators(self, request, queryset):
        """Make selected users administrators."""
        updated = queryset.update(role=User.Role.ADMINISTRATOR)
        self.message_user(
            request,
            f'{updated} user(s) were successfully made administrators.'
        )
    make_administrators.short_description = "Make selected users administrators"
    
    def make_brand_managers(self, request, queryset):
        """Make selected users brand managers."""
        updated = queryset.update(role=User.Role.BRAND_MANAGER)
        self.message_user(
            request,
            f'{updated} user(s) were successfully made brand managers.'
        )
    make_brand_managers.short_description = "Make selected users brand managers"
    
    def make_store_managers(self, request, queryset):
        """Make selected users store managers."""
        updated = queryset.update(role=User.Role.STORE_MANAGER)
        self.message_user(
            request,
            f'{updated} user(s) were successfully made store managers.'
        )
    make_store_managers.short_description = "Make selected users store managers"
    
    def get_queryset(self, request):
        """Filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        
        # Superusers can see all users
        if request.user.is_superuser:
            return qs
        
        # Regular admin users can only see users they can manage
        if hasattr(request.user, 'can_manage_user'):
            # This is a simplified version - in practice, you might want more complex logic
            return qs.filter(is_superuser=False)
        
        return qs
    
    def has_add_permission(self, request):
        """Check if user can add new users."""
        return request.user.is_superuser or request.user.is_administrator
    
    def has_change_permission(self, request, obj=None):
        """Check if user can change users."""
        if request.user.is_superuser:
            return True
        
        if obj is None:
            return request.user.is_authenticated
        
        # Users can always edit themselves
        if obj == request.user:
            return True
        
        # Check if user can manage the target user
        if hasattr(request.user, 'can_manage_user'):
            return request.user.can_manage_user(obj)
        
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Check if user can delete users."""
        if request.user.is_superuser:
            return True
        
        if obj is None:
            return False
        
        # Users cannot delete themselves
        if obj == request.user:
            return False
        
        # Check if user can manage the target user
        if hasattr(request.user, 'can_manage_user'):
            return request.user.can_manage_user(obj)
        
        return False
