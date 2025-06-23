"""
Unit tests for the stores app API views.
"""

from django.test import TestCase
from django.contrib.gis.geos import Point, Polygon
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from django.contrib.auth.models import User

from backend.apps.stores.models import District, Store, Inventory


class DistrictViewSetTest(APITestCase):
    """Test cases for DistrictViewSet."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        self.district = District.objects.create(
            name='Test District',
            code='TD',
            city='Ho Chi Minh City',
            population=200000,
            area_km2=Decimal('7.73'),
            district_type='urban',
            avg_income=Decimal('25000000'),
            is_active=True
        )
        
        self.list_url = reverse('stores:district-list')
        self.detail_url = reverse('stores:district-detail', args=[self.district.id])
    
    def test_list_districts(self):
        """Test listing districts."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test District')
    
    def test_retrieve_district(self):
        """Test retrieving a single district."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test District')
        self.assertEqual(response.data['code'], 'TD')
    
    def test_create_district(self):
        """Test creating a new district."""
        data = {
            'name': 'New District',
            'code': 'ND',
            'city': 'Ho Chi Minh City',
            'population': 150000,
            'area_km2': '5.5',
            'district_type': 'suburban',
            'avg_income': '20000000',
            'is_active': True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(District.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New District')
    
    def test_update_district(self):
        """Test updating a district."""
        data = {'name': 'Updated District'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated District')
    
    def test_delete_district(self):
        """Test deleting a district."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(District.objects.count(), 0)
    
    def test_search_districts(self):
        """Test searching districts."""
        url = f"{self.list_url}search/"
        response = self.client.get(url, {'district_name': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_district_statistics(self):
        """Test district statistics endpoint."""
        url = f"{self.list_url}statistics/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_districts'], 1)
        self.assertEqual(response.data['active_districts'], 1)


class StoreViewSetTest(APITestCase):
    """Test cases for StoreViewSet."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        self.district = District.objects.create(
            name='Test District',
            code='TD',
            city='Ho Chi Minh City'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test Street, Ho Chi Minh City',
            phone='+84-123-456-789',
            email='test@store.com',
            store_type='convenience',
            district='Test District',
            district_obj=self.district,
            city='Ho Chi Minh City',
            opening_hours='8:00-22:00',
            is_active=True,
            rating=Decimal('4.5'),
            location=Point(106.7, 10.8, srid=4326)
        )
        
        self.list_url = reverse('stores:store-list')
        self.detail_url = reverse('stores:store-detail', args=[self.store.id])
    
    def test_list_stores(self):
        """Test listing stores."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Store')
    
    def test_retrieve_store(self):
        """Test retrieving a single store."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Store')
        self.assertEqual(response.data['store_type'], 'convenience')
    
    def test_create_store(self):
        """Test creating a new store."""
        data = {
            'name': 'New Store',
            'address': '456 New Street, Ho Chi Minh City',
            'phone': '+84-987-654-321',
            'email': 'new@store.com',
            'store_type': 'supermarket',
            'district': 'Test District',
            'district_obj_id': self.district.id,
            'city': 'Ho Chi Minh City',
            'opening_hours': '7:00-23:00',
            'is_active': True,
            'rating': '4.0'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Store.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Store')
    
    def test_update_store(self):
        """Test updating a store."""
        data = {'name': 'Updated Store'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Store')
    
    def test_delete_store(self):
        """Test deleting a store."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Store.objects.count(), 0)
    
    def test_nearby_stores(self):
        """Test finding nearby stores."""
        url = f"{self.list_url}nearby/"
        response = self.client.get(url, {
            'latitude': 10.8,
            'longitude': 106.7,
            'radius_km': 5.0
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_stores_in_district(self):
        """Test finding stores in a district."""
        url = f"{self.list_url}in-district/"
        response = self.client.get(url, {'district_id': self.district.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_store_statistics(self):
        """Test store statistics endpoint."""
        url = f"{self.list_url}statistics/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_stores'], 1)
        self.assertEqual(response.data['active_stores'], 1)
    
    def test_store_inventory(self):
        """Test getting store inventory."""
        url = f"{self.detail_url}inventory/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)  # No inventory items yet


class InventoryViewSetTest(APITestCase):
    """Test cases for InventoryViewSet."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
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
            location=Point(106.7, 10.8, srid=4326)
        )
        
        self.inventory = Inventory.objects.create(
            store=self.store,
            item_name='Test Product',
            quantity=100,
            unit='pieces',
            price=Decimal('15000'),
            category='beverages',
            is_available=True
        )
        
        self.list_url = reverse('stores:inventory-list')
        self.detail_url = reverse('stores:inventory-detail', args=[self.inventory.id])
    
    def test_list_inventory(self):
        """Test listing inventory items."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['item_name'], 'Test Product')
    
    def test_retrieve_inventory(self):
        """Test retrieving a single inventory item."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_name'], 'Test Product')
        self.assertEqual(response.data['quantity'], 100)
    
    def test_create_inventory(self):
        """Test creating a new inventory item."""
        data = {
            'store_id': self.store.id,
            'item_name': 'New Product',
            'quantity': 50,
            'unit': 'pieces',
            'price': '20000',
            'category': 'snacks',
            'is_available': True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inventory.objects.count(), 2)
        self.assertEqual(response.data['item_name'], 'New Product')
    
    def test_update_inventory(self):
        """Test updating an inventory item."""
        data = {'quantity': 150}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 150)
    
    def test_delete_inventory(self):
        """Test deleting an inventory item."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Inventory.objects.count(), 0)
    
    def test_nearby_inventory(self):
        """Test finding nearby inventory items."""
        url = f"{self.list_url}nearby/"
        response = self.client.get(url, {
            'latitude': 10.8,
            'longitude': 106.7,
            'radius_km': 5.0
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_inventory(self):
        """Test searching inventory items."""
        url = f"{self.list_url}search/"
        response = self.client.get(url, {'item_name': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_inventory_statistics(self):
        """Test inventory statistics endpoint."""
        url = f"{self.list_url}statistics/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 1)
        self.assertEqual(response.data['available_items'], 1)


class APIFilteringTest(APITestCase):
    """Test cases for API filtering and search functionality."""
    
    def setUp(self):
        """Set up test data for filtering tests."""
        self.district1 = District.objects.create(
            name='District 1',
            code='D1',
            city='Ho Chi Minh City',
            district_type='urban',
            is_active=True
        )
        
        self.district2 = District.objects.create(
            name='District 2',
            code='D2',
            city='Ho Chi Minh City',
            district_type='suburban',
            is_active=True
        )
        
        self.store1 = Store.objects.create(
            name='Store 1',
            address='Address 1',
            store_type='convenience',
            district='District 1',
            district_obj=self.district1,
            city='Ho Chi Minh City',
            is_active=True
        )
        
        self.store2 = Store.objects.create(
            name='Store 2',
            address='Address 2',
            store_type='supermarket',
            district='District 2',
            district_obj=self.district2,
            city='Ho Chi Minh City',
            is_active=True
        )
    
    def test_filter_stores_by_type(self):
        """Test filtering stores by store type."""
        url = reverse('stores:store-list')
        response = self.client.get(url, {'store_type': 'convenience'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Store 1')
    
    def test_search_stores_by_name(self):
        """Test searching stores by name."""
        url = reverse('stores:store-list')
        response = self.client.get(url, {'search': 'Store 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Store 1')
    
    def test_filter_districts_by_type(self):
        """Test filtering districts by district type."""
        url = reverse('stores:district-list')
        response = self.client.get(url, {'district_type': 'urban'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'District 1')
    
    def test_order_stores_by_name(self):
        """Test ordering stores by name."""
        url = reverse('stores:store-list')
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'Store 1')
        self.assertEqual(response.data['results'][1]['name'], 'Store 2')


class APIErrorHandlingTest(APITestCase):
    """Test cases for API error handling."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
    
    def test_invalid_spatial_search(self):
        """Test invalid spatial search parameters."""
        url = reverse('stores:store-list') + 'nearby/'
        response = self.client.get(url, {
            'latitude': 100.0,  # Invalid latitude
            'longitude': 106.7,
            'radius_km': 5.0
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_district_search(self):
        """Test invalid district search parameters."""
        url = reverse('stores:district-list') + 'search/'
        response = self.client.get(url)  # No parameters
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_nonexistent_store(self):
        """Test accessing a non-existent store."""
        url = reverse('stores:store-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_store_data(self):
        """Test creating a store with invalid data."""
        url = reverse('stores:store-list')
        data = {
            'name': '',  # Invalid: empty name
            'store_type': 'invalid_type'  # Invalid: not in choices
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 