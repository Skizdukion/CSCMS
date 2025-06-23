from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point, Polygon
from django.core.validators import MinValueValidator, MaxValueValidator

class District(models.Model):
    """District model with geographic boundaries for spatial analysis"""
    
    # Basic district information
    name = models.CharField(max_length=100, unique=True, help_text="District name")
    code = models.CharField(max_length=10, unique=True, help_text="District code/abbreviation")
    
    # Geographic boundaries
    boundary = gis_models.PolygonField(
        help_text="Geographic boundary of the district",
        spatial_index=True,
        null=True,
        blank=True
    )
    
    # Administrative information
    city = models.CharField(max_length=100, default="Ho Chi Minh City", help_text="City name")
    population = models.IntegerField(
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)],
        help_text="District population"
    )
    area_km2 = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)],
        help_text="District area in square kilometers"
    )
    
    # District characteristics
    district_type = models.CharField(
        max_length=50,
        choices=[
            ('urban', 'Urban District'),
            ('suburban', 'Suburban District'),
            ('rural', 'Rural District'),
            ('industrial', 'Industrial District'),
            ('tourist', 'Tourist District'),
            ('other', 'Other')
        ],
        default='urban',
        help_text="Type of district"
    )
    
    # Economic indicators
    avg_income = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)],
        help_text="Average income in VND"
    )
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Whether the district is active")  # type: ignore[assignment]
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stores_district'
        verbose_name = 'District'
        verbose_name_plural = 'Districts'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['district_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['city', 'district_type']),
            models.Index(fields=['is_active', 'district_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def contains_point(self, point):
        """Check if a point is within this district's boundary"""
        if self.boundary and point:
            return self.boundary.contains(point)  # type: ignore[attr-defined]
        return False
    
    def get_stores(self):
        """Get all stores within this district"""
        if self.boundary:
            return Store.objects.filter(location__within=self.boundary)  # type: ignore[attr-defined]
        return Store.objects.filter(district=self.name)  # type: ignore[attr-defined]
    
    def get_store_count(self):
        """Get the number of stores in this district"""
        return self.get_stores().count()
    
    def get_area_centroid(self):
        """Get the centroid of the district boundary"""
        if self.boundary:
            return self.boundary.centroid  # type: ignore[attr-defined]
        return None

class Store(models.Model):
    """Store model with spatial fields for geographic location"""
    
    # Basic store information
    name = models.CharField(max_length=255, help_text="Store name")
    address = models.TextField(help_text="Full address of the store")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Contact phone number")
    email = models.EmailField(blank=True, null=True, help_text="Contact email")
    
    # Spatial fields
    location = gis_models.PointField(
        help_text="Geographic coordinates (latitude, longitude)",
        spatial_index=True,
        null=True,
        blank=True
    )
    
    # Store details
    store_type = models.CharField(
        max_length=50,
        choices=[
            ('convenience', 'Convenience Store'),
            ('gas_station', 'Gas Station'),
            ('supermarket', 'Supermarket'),
            ('pharmacy', 'Pharmacy'),
            ('other', 'Other')
        ],
        default='convenience',
        help_text="Type of store"
    )
    
    district = models.CharField(max_length=100, blank=True, null=True, help_text="District name")
    district_obj = models.ForeignKey(
        District, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='stores',
        help_text="District object reference"
    )
    city = models.CharField(max_length=100, default="Ho Chi Minh City", help_text="City name")
    
    # Operational information
    opening_hours = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Store opening hours (e.g., '8:00-22:00')"
    )
    is_active = models.BooleanField(default=True, help_text="Whether the store is currently active")  # type: ignore[assignment]
    
    # Performance metrics
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank=True, 
        null=True, 
        help_text="Store rating (0-5)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stores_store'
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['district']),
            models.Index(fields=['store_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['city', 'district']),
            models.Index(fields=['store_type', 'is_active']),
            models.Index(fields=['district_obj', 'store_type']),
            models.Index(fields=['is_active', 'store_type', 'city']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.address}"
    
    def save(self, *args, **kwargs):
        # Ensure location is properly set if coordinates are provided
        if hasattr(self, 'latitude') and hasattr(self, 'longitude'):
            if self.latitude and self.longitude:
                self.location = Point(self.longitude, self.latitude, srid=4326)
        super().save(*args, **kwargs)
    
    @property
    def latitude(self):
        """Get latitude from PointField"""
        if self.location:
            return self.location.y  # type: ignore[attr-defined]
        return None
    
    @property
    def longitude(self):
        """Get longitude from PointField"""
        if self.location:
            return self.location.x  # type: ignore[attr-defined]
        return None
    
    def set_location(self, latitude, longitude):
        """Set location using latitude and longitude"""
        self.location = Point(longitude, latitude, srid=4326)
    
    def distance_to(self, other_point):
        """Calculate distance to another point in meters"""
        if self.location and other_point:
            return self.location.distance(other_point) * 111320  # type: ignore[attr-defined] # Convert degrees to meters
        return None

class Inventory(models.Model):
    """Inventory model for store items"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventories')
    item_name = models.CharField(max_length=255, help_text="Name of the inventory item")
    quantity = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Current quantity in stock"
    )
    unit = models.CharField(
        max_length=20,
        choices=[
            ('pieces', 'Pieces'),
            ('kg', 'Kilograms'),
            ('liters', 'Liters'),
            ('boxes', 'Boxes'),
            ('packs', 'Packs'),
            ('other', 'Other')
        ],
        default='pieces',
        help_text="Unit of measurement"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Price per unit"
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('beverages', 'Beverages'),
            ('snacks', 'Snacks'),
            ('dairy', 'Dairy'),
            ('frozen', 'Frozen Foods'),
            ('household', 'Household'),
            ('personal_care', 'Personal Care'),
            ('other', 'Other')
        ],
        default='other',
        help_text="Item category"
    )
    is_available = models.BooleanField(default=True, help_text="Whether the item is available for sale")  # type: ignore[assignment]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stores_inventory'
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
        ordering = ['store', 'category', 'item_name']
        indexes = [
            models.Index(fields=['store', 'category']),
            models.Index(fields=['is_available']),
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['store', 'is_available']),
            models.Index(fields=['category', 'unit']),
            models.Index(fields=['store', 'category', 'is_available']),
        ]
    
    def __str__(self):
        return f"{self.item_name} ({self.quantity} {self.unit}) at {self.store.name}" 