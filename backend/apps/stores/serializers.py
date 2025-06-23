from rest_framework import serializers
from .models import Store, Inventory, District

class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model with spatial fields"""
    store_count = serializers.SerializerMethodField()
    
    class Meta:
        model = District
        fields = [
            'id', 'name', 'code', 'boundary',
            'city', 'population', 'area_km2',
            'district_type', 'avg_income', 'is_active',
            'store_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_store_count(self, obj):
        """Get the number of stores in this district"""
        return obj.get_store_count()

class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model with spatial fields"""
    latitude = serializers.ReadOnlyField(source='latitude')
    longitude = serializers.ReadOnlyField(source='longitude')
    district_info = DistrictSerializer(source='district_obj', read_only=True)
    
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'address', 'phone', 'email',
            'location', 'latitude', 'longitude',
            'store_type', 'district', 'district_obj', 'district_info', 'city',
            'opening_hours', 'is_active', 'rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class InventorySerializer(serializers.ModelSerializer):
    """Serializer for Inventory model"""
    store_name = serializers.ReadOnlyField(source='store.name')
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'store', 'store_name', 'item_name', 'quantity', 'unit',
            'price', 'category', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class StoreDetailSerializer(StoreSerializer):
    """Detailed serializer for Store model including inventory"""
    inventories = InventorySerializer(many=True, read_only=True)
    
    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + ['inventories'] 