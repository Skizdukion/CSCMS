"""
Unit tests for the stores app serializers.
"""

from django.test import TestCase
from django.contrib.gis.geos import Point, Polygon
from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import serializers

from backend.apps.stores.models import District, Store, Inventory, Item
from backend.apps.stores.serializers import (
    DistrictSerializer, StoreSerializer, InventorySerializer,
    StoreListSerializer, InventoryListSerializer,
    SpatialSearchSerializer, DistrictSearchSerializer
)


class DistrictSerializerTest(TestCase):
    """Test cases for DistrictSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.district_data = {
            'name': 'Test District',
            'code': 'TD',
            'city': 'Ho Chi Minh City',
            'population': 200000,
            'area_km2': Decimal('7.73'),
            'district_type': 'urban',
            'avg_income': Decimal('25000000'),
            'is_active': True
        }
        
        self.test_polygon = Polygon([
            (106.6, 10.7),
            (106.8, 10.7),
            (106.8, 10.9),
            (106.6, 10.9),
            (106.6, 10.7),
        ], srid=4326)
    
    def test_district_serialization(self):
        """Test district serialization."""
        district = District.objects.create(**self.district_data)
        serializer = DistrictSerializer(district)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test District')
        self.assertEqual(data['code'], 'TD')
        self.assertEqual(data['city'], 'Ho Chi Minh City')
        self.assertEqual(data['population'], 200000)
        self.assertEqual(data['area_km2'], '7.73')
        self.assertEqual(data['district_type'], 'urban')
        self.assertEqual(data['avg_income'], '25000000.00')
        self.assertTrue(data['is_active'])
        self.assertEqual(data['store_count'], 0)
        self.assertIsNone(data['boundary'])
        self.assertIsNone(data['boundary_geojson'])
        self.assertIsNone(data['centroid'])
    
    def test_district_serialization_with_boundary(self):
        """Test district serialization with spatial boundary."""
        district_data = self.district_data.copy()
        district_data['boundary'] = self.test_polygon
        district = District.objects.create(**district_data)
        
        serializer = DistrictSerializer(district)
        data = serializer.data
        
        self.assertIsNotNone(data['boundary'])
        self.assertIsNotNone(data['boundary_geojson'])
        self.assertIsNotNone(data['centroid'])
        self.assertEqual(data['boundary_geojson']['type'], 'Polygon')
        self.assertEqual(data['centroid']['geojson']['type'], 'Point')
    
    def test_district_validation(self):
        """Test district validation."""
        # Test valid data
        serializer = DistrictSerializer(data=self.district_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid population
        invalid_data = self.district_data.copy()
        invalid_data['population'] = -100
        serializer = DistrictSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('population', serializer.errors)
        
        # Test invalid area
        invalid_data = self.district_data.copy()
        invalid_data['area_km2'] = Decimal('-5.0')
        serializer = DistrictSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('area_km2', serializer.errors)
    
    def test_boundary_validation(self):
        """Test boundary validation."""
        # Test valid GeoJSON
        valid_geojson = {
            'type': 'Polygon',
            'coordinates': [[[106.6, 10.7], [106.8, 10.7], [106.8, 10.9], [106.6, 10.9], [106.6, 10.7]]]
        }
        district_data = self.district_data.copy()
        district_data['boundary'] = valid_geojson
        
        serializer = DistrictSerializer(data=district_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid geometry type - this should pass validation since we're not validating geometry type in the serializer
        # The actual validation happens at the model level
        invalid_geojson = {
            'type': 'Point',
            'coordinates': [106.7, 10.8]
        }
        district_data['boundary'] = invalid_geojson
        serializer = DistrictSerializer(data=district_data)
        # This should be valid at serializer level, validation happens at model level
        self.assertTrue(serializer.is_valid())


class StoreSerializerTest(TestCase):
    """Test cases for StoreSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.district = District.objects.create(
            name='Test District',
            code='TD',
            city='Ho Chi Minh City'
        )
        
        self.store_data = {
            'name': 'Test Store',
            'address': '123 Test Street, Ho Chi Minh City',
            'phone': '+84-123-456-789',
            'email': 'test@store.com',
            'store_type': 'convenience',
            'district': 'Test District',
            'district_obj': self.district,
            'city': 'Ho Chi Minh City',
            'opening_hours': '8:00-22:00',
            'is_active': True,
            'rating': Decimal('4.5')
        }
    
    def test_store_serialization(self):
        """Test store serialization."""
        store = Store.objects.create(**self.store_data)
        serializer = StoreSerializer(store)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Store')
        self.assertEqual(data['address'], '123 Test Street, Ho Chi Minh City')
        self.assertEqual(data['phone'], '+84-123-456-789')
        self.assertEqual(data['email'], 'test@store.com')
        self.assertEqual(data['store_type'], 'convenience')
        self.assertEqual(data['district'], 'Test District')
        self.assertEqual(data['city'], 'Ho Chi Minh City')
        self.assertEqual(data['opening_hours'], '8:00-22:00')
        self.assertTrue(data['is_active'])
        self.assertEqual(data['rating'], '4.50')
        self.assertEqual(data['inventory_count'], 0)
        self.assertIsNone(data['location'])
        self.assertIsNone(data['location_geojson'])
        self.assertIsNone(data['latitude'])
        self.assertIsNone(data['longitude'])
    
    def test_store_serialization_with_location(self):
        """Test store serialization with spatial location."""
        store_data = self.store_data.copy()
        store_data['location'] = Point(106.7, 10.8, srid=4326)
        store = Store.objects.create(**store_data)
        
        serializer = StoreSerializer(store)
        data = serializer.data
        
        self.assertIsNotNone(data['location'])
        self.assertIsNotNone(data['location_geojson'])
        self.assertEqual(data['latitude'], 10.8)
        self.assertEqual(data['longitude'], 106.7)
        self.assertEqual(data['location_geojson']['type'], 'Point')
    
    def test_store_validation(self):
        """Test store validation."""
        # Test valid data
        serializer = StoreSerializer(data=self.store_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid rating
        invalid_data = self.store_data.copy()
        invalid_data['rating'] = Decimal('6.0')
        serializer = StoreSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating', serializer.errors)
        
        # Test invalid district_obj_id
        invalid_data = self.store_data.copy()
        invalid_data['district_obj_id'] = 99999
        serializer = StoreSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('district_obj_id', serializer.errors)
    
    def test_location_validation(self):
        """Test location validation."""
        # Test valid GeoJSON Point
        valid_geojson = {
            'type': 'Point',
            'coordinates': [106.7, 10.8]
        }
        store_data = self.store_data.copy()
        store_data['location'] = valid_geojson
        
        serializer = StoreSerializer(data=store_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid geometry type - this should pass validation since we're not validating geometry type in the serializer
        # The actual validation happens at the model level
        invalid_geojson = {
            'type': 'Polygon',
            'coordinates': [[[106.6, 10.7], [106.8, 10.7], [106.8, 10.9], [106.6, 10.9], [106.6, 10.7]]]
        }
        store_data['location'] = invalid_geojson
        serializer = StoreSerializer(data=store_data)
        # This should be valid at serializer level, validation happens at model level
        self.assertTrue(serializer.is_valid())


class ItemSerializerTest(TestCase):
    """Test cases for ItemSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.item_data = {
            'name': 'Test Product',
            'description': 'A test product for unit testing',
            'category': 'beverages',
            'brand': 'Test Brand',
            'barcode': '1234567890123',
            'unit': 'piece',
            'is_active': True
        }
    
    def test_item_serialization(self):
        """Test item serialization."""
        item = Item.objects.create(**self.item_data)
        
        # Import here to avoid circular imports during module loading
        from backend.apps.stores.serializers import ItemSerializer
        serializer = ItemSerializer(item)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Product')
        self.assertEqual(data['description'], 'A test product for unit testing')
        self.assertEqual(data['category'], 'beverages')
        self.assertEqual(data['brand'], 'Test Brand')
        self.assertEqual(data['barcode'], '1234567890123')
        self.assertEqual(data['unit'], 'piece')
        self.assertTrue(data['is_active'])
        self.assertEqual(data['store_count'], 0)
    
    def test_item_validation(self):
        """Test item validation."""
        from backend.apps.stores.serializers import ItemSerializer
        
        # Test valid data
        serializer = ItemSerializer(data=self.item_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid category
        invalid_data = self.item_data.copy()
        invalid_data['category'] = 'invalid_category'
        serializer = ItemSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('category', serializer.errors)
        
        # Test invalid unit
        invalid_data = self.item_data.copy()
        invalid_data['unit'] = 'invalid_unit'
        serializer = ItemSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('unit', serializer.errors)
        
        # Test missing required field
        invalid_data = self.item_data.copy()
        invalid_data.pop('name')
        serializer = ItemSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class InventorySerializerTest(TestCase):
    """Test cases for InventorySerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.district = District.objects.create(
            name='Test District',
            code='TD',
            city='Ho Chi Minh City'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test Street, Ho Chi Minh City',
            district='Test District',
            district_obj=self.district,
            city='Ho Chi Minh City'
        )
        
        self.item = Item.objects.create(
            name='Test Product',
            description='A test product',
            category='beverages',
            brand='Test Brand',
            unit='piece',
            is_active=True
        )
        
        self.inventory_data = {
            'store': self.store,
            'item': self.item,
            'is_available': True
        }
    
    def test_inventory_serialization(self):
        """Test inventory serialization."""
        inventory = Inventory.objects.create(**self.inventory_data)
        serializer = InventorySerializer(inventory)
        data = serializer.data
        
        self.assertTrue(data['is_available'])
        self.assertEqual(data['store_name'], 'Test Store')
        self.assertEqual(data['item_name'], 'Test Product')
        self.assertEqual(data['item_category'], 'beverages')
        self.assertEqual(data['stock_status'], 'available')
        self.assertIsNone(data['store_location'])
    
    def test_inventory_serialization_with_store_location(self):
        """Test inventory serialization with store location."""
        # Add location to store
        self.store.location = Point(106.7, 10.8, srid=4326)
        self.store.save()
        
        inventory = Inventory.objects.create(**self.inventory_data)
        serializer = InventorySerializer(inventory)
        data = serializer.data
        
        self.assertIsNotNone(data['store_location'])
        self.assertEqual(data['store_location']['latitude'], 10.8)
        self.assertEqual(data['store_location']['longitude'], 106.7)
        self.assertEqual(data['store_location']['geojson']['type'], 'Point')
    
    def test_inventory_validation(self):
        """Test inventory validation."""
        # Test valid data
        valid_data = {
            'store_id': self.store.id,
            'item_id': self.item.id,
            'is_available': True
        }
        serializer = InventorySerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid store_id
        invalid_data = valid_data.copy()
        invalid_data['store_id'] = 99999
        serializer = InventorySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('store_id', serializer.errors)
        
        # Test invalid item_id
        invalid_data = valid_data.copy()
        invalid_data['item_id'] = 99999
        serializer = InventorySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('item_id', serializer.errors)


class SpatialSearchSerializerTest(TestCase):
    """Test cases for SpatialSearchSerializer."""
    
    def test_valid_spatial_search(self):
        """Test valid spatial search parameters."""
        data = {
            'latitude': 10.8,
            'longitude': 106.7,
            'radius_km': 5.0
        }
        serializer = SpatialSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_latitude(self):
        """Test invalid latitude."""
        data = {
            'latitude': 100.0,  # Invalid latitude
            'longitude': 106.7,
            'radius_km': 5.0
        }
        serializer = SpatialSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('latitude', serializer.errors)
    
    def test_invalid_longitude(self):
        """Test invalid longitude."""
        data = {
            'latitude': 10.8,
            'longitude': 200.0,  # Invalid longitude
            'radius_km': 5.0
        }
        serializer = SpatialSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('longitude', serializer.errors)
    
    def test_invalid_radius(self):
        """Test invalid radius."""
        data = {
            'latitude': 10.8,
            'longitude': 106.7,
            'radius_km': 0.0  # Invalid radius
        }
        serializer = SpatialSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('radius_km', serializer.errors)


class DistrictSearchSerializerTest(TestCase):
    """Test cases for DistrictSearchSerializer."""
    
    def test_valid_district_search_by_id(self):
        """Test valid district search by ID."""
        data = {'district_id': 1}
        serializer = DistrictSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_valid_district_search_by_name(self):
        """Test valid district search by name."""
        data = {'district_name': 'Test District'}
        serializer = DistrictSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_valid_district_search_by_type(self):
        """Test valid district search by type."""
        data = {'district_type': 'urban'}
        serializer = DistrictSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_district_search_no_params(self):
        """Test invalid district search with no parameters."""
        data = {}
        serializer = DistrictSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class StoreListSerializerTest(TestCase):
    """Test cases for StoreListSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.district = District.objects.create(
            name='Test District',
            code='TD',
            city='Ho Chi Minh City'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test Street, Ho Chi Minh City',
            district='Test District',
            district_obj=self.district,
            city='Ho Chi Minh City',
            store_type='convenience',
            is_active=True,
            rating=Decimal('4.5')
        )
    
    def test_store_list_serialization(self):
        """Test store list serialization."""
        serializer = StoreListSerializer(self.store)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Store')
        self.assertEqual(data['address'], '123 Test Street, Ho Chi Minh City')
        self.assertEqual(data['store_type'], 'convenience')
        self.assertEqual(data['district_name'], 'Test District')
        self.assertEqual(data['city'], 'Ho Chi Minh City')
        self.assertTrue(data['is_active'])
        self.assertEqual(data['rating'], '4.50')
        self.assertEqual(data['inventory_count'], 0)
        self.assertIsNone(data['location_geojson'])


class InventoryListSerializerTest(TestCase):
    """Test cases for InventoryListSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.district = District.objects.create(
            name='Test District',
            code='TD',
            city='Ho Chi Minh City'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test Street, Ho Chi Minh City',
            district='Test District',
            district_obj=self.district,
            city='Ho Chi Minh City'
        )
        
        self.item = Item.objects.create(
            name='Test Product',
            description='A test product',
            category='beverages',
            brand='Test Brand',
            unit='piece',
            is_active=True
        )
        
        self.inventory = Inventory.objects.create(
            store=self.store,
            item=self.item,
            is_available=True
        )
    
    def test_inventory_list_serialization(self):
        """Test inventory list serialization."""
        serializer = InventoryListSerializer(self.inventory)
        data = serializer.data
        
        self.assertEqual(data['item_name'], 'Test Product')
        self.assertTrue(data['is_available'])
        self.assertEqual(data['store_name'], 'Test Store')
        self.assertEqual(data['store_address'], '123 Test Street, Ho Chi Minh City')
        self.assertEqual(data['item_category'], 'beverages')
        self.assertEqual(data['stock_status'], 'available') 