"""
Django admin interface for the stores app with spatial data management.
"""

from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.geos import Point
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from django.contrib.admin import SimpleListFilter

from backend.apps.stores.models import District, Store, Item, Inventory


class DistrictTypeFilter(SimpleListFilter):
    """Filter districts by type."""
    title = 'District Type'
    parameter_name = 'district_type'

    def lookups(self, request, model_admin):
        return [
            ('urban', 'Urban District'),
            ('suburban', 'Suburban District'),
            ('rural', 'Rural District'),
            ('industrial', 'Industrial District'),
            ('tourist', 'Tourist District'),
            ('other', 'Other'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(district_type=self.value())


class StoreTypeFilter(SimpleListFilter):
    """Filter stores by type."""
    title = 'Store Type'
    parameter_name = 'store_type'

    def lookups(self, request, model_admin):
        return [
            ('convenience', 'Convenience Store'),
            ('gas_station', 'Gas Station'),
            ('supermarket', 'Supermarket'),
            ('pharmacy', 'Pharmacy'),
            ('other', 'Other'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(store_type=self.value())


class InventoryInline(admin.TabularInline):
    """Inline admin for inventory items."""
    model = Inventory
    extra = 1
    fields = ('item', 'is_available')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('item')


@admin.register(District)
class DistrictAdmin(OSMGeoAdmin):
    """Admin interface for District model with spatial support."""
    
    list_display = ('name', 'code', 'city', 'district_type', 'population', 'area_km2', 'store_count', 'is_active')
    list_filter = (DistrictTypeFilter, 'city', 'is_active', 'district_type')
    search_fields = ('name', 'code', 'city')
    readonly_fields = ('created_at', 'updated_at', 'store_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'city', 'district_type', 'is_active')
        }),
        ('Geographic Data', {
            'fields': ('boundary',),
            'classes': ('collapse',)
        }),
        ('Demographics', {
            'fields': ('population', 'area_km2', 'avg_income'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def store_count(self, obj):
        """Display the number of stores in this district."""
        count = obj.get_store_count()
        if count > 0:
            url = reverse('admin:stores_store_changelist') + f'?district_obj__id__exact={obj.id}'
            return format_html('<a href="{}">{} stores</a>', url, count)
        return '0 stores'
    store_count.short_description = 'Stores'
    
    def get_queryset(self, request):
        """Annotate queryset with store count."""
        return super().get_queryset(request).annotate(
            store_count=Count('stores')
        ).select_related()
    
    actions = ['activate_districts', 'deactivate_districts']
    
    def activate_districts(self, request, queryset):
        """Activate selected districts."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} districts were successfully activated.')
    activate_districts.short_description = "Activate selected districts"
    
    def deactivate_districts(self, request, queryset):
        """Deactivate selected districts."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} districts were successfully deactivated.')
    deactivate_districts.short_description = "Deactivate selected districts"


@admin.register(Store)
class StoreAdmin(OSMGeoAdmin):
    """Admin interface for Store model with spatial support."""
    
    list_display = ('name', 'district', 'store_type', 'city', 'location_display', 'rating', 'is_active', 'inventory_count')
    list_filter = (StoreTypeFilter, 'district', 'city', 'is_active', 'store_type')
    search_fields = ('name', 'address', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'inventory_count', 'latitude', 'longitude')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'phone', 'email', 'store_type', 'is_active')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude', 'district', 'district_obj', 'city')
        }),
        ('Operational Details', {
            'fields': ('opening_hours', 'rating'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [InventoryInline]
    
    def location_display(self, obj):
        """Display location coordinates."""
        if obj.location:
            return f"{obj.latitude:.4f}, {obj.longitude:.4f}"
        return "No location"
    location_display.short_description = 'Coordinates'
    
    def inventory_count(self, obj):
        """Display the number of inventory items."""
        count = obj.inventories.count()
        if count > 0:
            url = reverse('admin:stores_inventory_changelist') + f'?store__id__exact={obj.id}'
            return format_html('<a href="{}">{} items</a>', url, count)
        return '0 items'
    inventory_count.short_description = 'Inventory Items'
    
    def get_queryset(self, request):
        """Annotate queryset with inventory count."""
        return super().get_queryset(request).annotate(
            inventory_count=Count('inventories')
        ).select_related('district_obj')
    
    actions = ['activate_stores', 'deactivate_stores', 'set_location_from_coordinates']
    
    def activate_stores(self, request, queryset):
        """Activate selected stores."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} stores were successfully activated.')
    activate_stores.short_description = "Activate selected stores"
    
    def deactivate_stores(self, request, queryset):
        """Deactivate selected stores."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} stores were successfully deactivated.')
    deactivate_stores.short_description = "Deactivate selected stores"
    
    def set_location_from_coordinates(self, request, queryset):
        """Set location from latitude/longitude fields."""
        updated = 0
        for store in queryset:
            if hasattr(store, 'latitude') and hasattr(store, 'longitude'):
                if store.latitude and store.longitude:
                    store.location = Point(store.longitude, store.latitude, srid=4326)
                    store.save()
                    updated += 1
        self.message_user(request, f'Location set for {updated} stores.')
    set_location_from_coordinates.short_description = "Set location from coordinates"


class InventoryCategoryFilter(SimpleListFilter):
    """Filter inventory by category."""
    title = 'Category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [
            ('beverages', 'Beverages'),
            ('snacks', 'Snacks'),
            ('dairy', 'Dairy'),
            ('frozen', 'Frozen Foods'),
            ('household', 'Household'),
            ('personal_care', 'Personal Care'),
            ('other', 'Other'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(item__category=self.value())


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin interface for Item model."""
    
    list_display = ('name', 'category', 'brand', 'store_count', 'is_active')
    list_filter = ('category', 'is_active', 'brand')
    search_fields = ('name', 'description', 'brand', 'barcode')
    readonly_fields = ('created_at', 'updated_at', 'store_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'brand', 'is_active')
        }),
        ('Product Details', {
            'fields': ('barcode',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def store_count(self, obj):
        """Display the number of stores that stock this item."""
        count = obj.get_store_count()
        if count > 0:
            url = reverse('admin:stores_inventory_changelist') + f'?item__id__exact={obj.id}'
            return format_html('<a href="{}">{} stores</a>', url, count)
        return '0 stores'
    store_count.short_description = 'Stores'
    
    actions = ['activate_items', 'deactivate_items']
    
    def activate_items(self, request, queryset):
        """Activate selected items."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} items were successfully activated.')
    activate_items.short_description = "Activate selected items"
    
    def deactivate_items(self, request, queryset):
        """Deactivate selected items."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} items were successfully deactivated.')
    deactivate_items.short_description = "Deactivate selected items"


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    """Admin interface for Inventory model."""
    
    list_display = ('item', 'store', 'stock_status', 'is_available', 'store_location')
    list_filter = (InventoryCategoryFilter, 'is_available', 'store__district', 'store__store_type')
    search_fields = ('item__name', 'store__name', 'store__address')
    readonly_fields = ('created_at', 'updated_at', 'store_location', 'stock_status')
    
    fieldsets = (
        ('Inventory Information', {
            'fields': ('item', 'store', 'is_available')
        }),
        ('Status', {
            'fields': ('stock_status', 'store_location'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def store_location(self, obj):
        """Display store location information."""
        if obj.store and obj.store.location:
            return f"{obj.store.latitude:.4f}, {obj.store.longitude:.4f}"
        return "No location"
    store_location.short_description = 'Store Location'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('item', 'store')
    
    actions = ['mark_available', 'mark_unavailable']
    
    def mark_available(self, request, queryset):
        """Mark selected items as available."""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} items were marked as available.')
    mark_available.short_description = "Mark items as available"
    
    def mark_unavailable(self, request, queryset):
        """Mark selected items as unavailable."""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} items were marked as unavailable.')
    mark_unavailable.short_description = "Mark items as unavailable"


# Customize admin site
admin.site.site_header = "Convenience Store Management System"
admin.site.site_title = "CSCMS Admin"
admin.site.index_title = "Welcome to CSCMS Administration" 