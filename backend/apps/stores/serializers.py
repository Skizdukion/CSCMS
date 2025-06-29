"""
Django REST framework serializers for the stores app with spatial data support.
"""

from rest_framework import serializers
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

from backend.apps.stores.models import District, Store, Inventory


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model with spatial boundary support."""
    
    # Spatial field serialization
    boundary = serializers.SerializerMethodField()
    boundary_geojson = serializers.SerializerMethodField()
    
    # Computed fields
    store_count = serializers.SerializerMethodField()
    centroid = serializers.SerializerMethodField()
    
    class Meta:
        model = District
        fields = [
            'id', 'name', 'code', 'city', 'population', 'area_km2',
            'district_type', 'avg_income', 'is_active', 'boundary',
            'boundary_geojson', 'store_count', 'centroid',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'store_count', 'centroid']
    
    def get_boundary(self, obj):
        """Return boundary as WKT (Well-Known Text) format."""
        if obj.boundary:
            return obj.boundary.wkt
        return None
    
    def get_boundary_geojson(self, obj):
        """Return boundary as GeoJSON format."""
        if obj.boundary:
            return json.loads(obj.boundary.json)
        return None
    
    def get_store_count(self, obj):
        """Return the number of stores in this district."""
        return obj.get_store_count()
    
    def get_centroid(self, obj):
        """Return the centroid of the district boundary."""
        centroid = obj.get_area_centroid()
        if centroid:
            return {
                'latitude': centroid.y,
                'longitude': centroid.x,
                'geojson': json.loads(centroid.json)
            }
        return None
    
    def validate_boundary(self, value):
        """Validate boundary data if provided."""
        if value:
            try:
                if isinstance(value, str):
                    # Try to parse as WKT or GeoJSON
                    if value.startswith('{'):
                        # GeoJSON
                        geom = GEOSGeometry(value)
                    else:
                        # WKT
                        geom = GEOSGeometry(value)
                else:
                    geom = value
                
                if geom.geom_type != 'Polygon':
                    raise ValidationError("Boundary must be a Polygon geometry.")
                
                return geom
            except Exception as e:
                raise ValidationError(f"Invalid boundary geometry: {str(e)}")
        return value
    
    def validate_population(self, value):
        """Validate population is non-negative."""
        if value is not None and value < 0:
            raise ValidationError("Population cannot be negative.")
        return value
    
    def validate_area_km2(self, value):
        """Validate area is positive."""
        if value is not None and value <= 0:
            raise ValidationError("Area must be positive.")
        return value
    
    def validate_avg_income(self, value):
        """Validate average income is non-negative."""
        if value is not None and value < 0:
            raise ValidationError("Average income cannot be negative.")
        return value


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model with spatial location support."""
    
    # Spatial field serialization
    location = serializers.SerializerMethodField()
    location_geojson = serializers.SerializerMethodField()
    
    # Related fields
    district_obj = DistrictSerializer(read_only=True)
    district_obj_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Computed fields
    inventory_count = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'address', 'phone', 'email', 'store_type',
            'district', 'district_obj', 'district_obj_id', 'city',
            'opening_hours', 'is_active', 'rating', 'location',
            'location_geojson', 'latitude', 'longitude', 'inventory_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'inventory_count']
    
    def get_location(self, obj):
        """Return location as WKT format."""
        if obj.location:
            return obj.location.wkt
        return None
    
    def get_location_geojson(self, obj):
        """Return location as GeoJSON format."""
        if obj.location:
            return json.loads(obj.location.json)
        return None
    
    def get_latitude(self, obj):
        """Return latitude coordinate."""
        return obj.latitude
    
    def get_longitude(self, obj):
        """Return longitude coordinate."""
        return obj.longitude
    
    def get_inventory_count(self, obj):
        """Return the number of inventory items."""
        return obj.inventories.count()
    
    def validate_location(self, value):
        """Validate location data if provided."""
        if value:
            try:
                if isinstance(value, str):
                    # Try to parse as WKT or GeoJSON
                    if value.startswith('{'):
                        # GeoJSON
                        geom = GEOSGeometry(value)
                    else:
                        # WKT
                        geom = GEOSGeometry(value)
                else:
                    geom = value
                
                if geom.geom_type != 'Point':
                    raise ValidationError("Location must be a Point geometry.")
                
                return geom
            except Exception as e:
                raise ValidationError(f"Invalid location geometry: {str(e)}")
        return value
    
    def validate_rating(self, value):
        """Validate rating is between 0 and 5."""
        if value is not None:
            if value < 0 or value > 5:
                raise ValidationError("Rating must be between 0 and 5.")
        return value
    
    def validate_district_obj_id(self, value):
        """Validate district_obj_id exists."""
        if value is not None:
            if not District.objects.filter(id=value).exists():  
                raise ValidationError("District with this ID does not exist.")
        return value


class StoreListSerializer(serializers.ModelSerializer):
    """Simplified serializer for store listing with consistent fields."""
    
    # Spatial field serialization
    location = serializers.SerializerMethodField()
    location_geojson = serializers.SerializerMethodField()
    
    # Related fields
    district_obj = DistrictSerializer(read_only=True)
    district_name = serializers.CharField(source='district_obj.name', read_only=True)
    
    # Computed fields
    inventory_count = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'address', 'phone', 'email', 'store_type',
            'district', 'district_obj', 'district_name', 'city',
            'opening_hours', 'is_active', 'rating', 'location',
            'location_geojson', 'latitude', 'longitude', 'inventory_count',
            'created_at', 'updated_at'
        ]
    
    def get_location(self, obj):
        """Return location as WKT format."""
        if obj.location:
            return obj.location.wkt
        return None
    
    def get_location_geojson(self, obj):
        """Return location as GeoJSON format."""
        if obj.location:
            return json.loads(obj.location.json)
        return None
    
    def get_latitude(self, obj):
        """Return latitude coordinate."""
        return obj.latitude
    
    def get_longitude(self, obj):
        """Return longitude coordinate."""
        return obj.longitude
    
    def get_inventory_count(self, obj):
        """Return the number of inventory items."""
        return obj.inventories.count()


class InventorySerializer(serializers.ModelSerializer):
    """Serializer for Inventory model."""
    
    # Related fields
    store = StoreSerializer(read_only=True)
    store_id = serializers.IntegerField(write_only=True)
    
    # Computed fields
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_location = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'store', 'store_id', 'store_name', 'item_name',
            'quantity', 'unit', 'price', 'category', 'is_available',
            'store_location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_store_location(self, obj):
        """Return store location information."""
        if obj.store and obj.store.location:
            return {
                'latitude': obj.store.latitude,
                'longitude': obj.store.longitude,
                'geojson': json.loads(obj.store.location.json)
            }
        return None
    
    def validate_quantity(self, value):
        """Validate quantity is non-negative."""
        if value < 0:
            raise ValidationError("Quantity cannot be negative.")
        return value
    
    def validate_price(self, value):
        """Validate price is non-negative."""
        if value is not None and value < 0:
            raise ValidationError("Price cannot be negative.")
        return value
    
    def validate_store_id(self, value):
        """Validate store_id exists."""
        if not Store.objects.filter(id=value).exists():  
            raise ValidationError("Store with this ID does not exist.")
        return value


class InventoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for inventory listing."""
    
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_address = serializers.CharField(source='store.address', read_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'item_name', 'quantity', 'unit', 'price',
            'category', 'is_available', 'store_name', 'store_address'
        ]


class SpatialSearchSerializer(serializers.Serializer):
    """Serializer for spatial search parameters."""
    
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    radius_km = serializers.FloatField(required=True, min_value=0.1, max_value=100.0)
    
    def validate_latitude(self, value):
        """Validate latitude is between -90 and 90."""
        if value < -90 or value > 90:
            raise ValidationError("Latitude must be between -90 and 90.")
        return value
    
    def validate_longitude(self, value):
        """Validate longitude is between -180 and 180."""
        if value < -180 or value > 180:
            raise ValidationError("Longitude must be between -180 and 180.")
        return value


class DistrictSearchSerializer(serializers.Serializer):
    """Serializer for district search parameters."""
    
    district_id = serializers.IntegerField(required=False)
    district_name = serializers.CharField(required=False, max_length=100)
    district_type = serializers.ChoiceField(
        choices=[('urban', 'Urban'), ('suburban', 'Suburban'), ('rural', 'Rural')],
        required=False
    )
    
    def validate(self, data):
        """Validate that at least one search parameter is provided."""
        if not any([data.get('district_id'), data.get('district_name'), data.get('district_type')]):
            raise ValidationError("At least one search parameter must be provided.")
        return data


class StoreStatisticsSerializer(serializers.Serializer):
    """Serializer for store statistics."""
    
    total_stores = serializers.IntegerField()
    active_stores = serializers.IntegerField()
    stores_by_type = serializers.DictField()
    stores_by_district = serializers.DictField()
    average_rating = serializers.FloatField()
    total_inventory_items = serializers.IntegerField()


class DistrictStatisticsSerializer(serializers.Serializer):
    """Serializer for district statistics."""
    
    total_districts = serializers.IntegerField()
    active_districts = serializers.IntegerField()
    districts_by_type = serializers.DictField()
    total_population = serializers.IntegerField()
    average_area = serializers.FloatField()
    average_income = serializers.FloatField() 