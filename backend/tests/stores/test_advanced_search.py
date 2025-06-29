"""
Unit tests for advanced store search functionality.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal

from backend.apps.stores.models import Store, District, Inventory


class AdvancedStoreSearchTest(APITestCase):
    """Test cases for advanced store search functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test districts
        self.district1 = District.objects.create(
            name="District 1",
            code="D1",
            city="Ho Chi Minh City",
            district_type="urban",
            is_active=True
        )
        
        self.district2 = District.objects.create(
            name="District 3",
            code="D3",
            city="Ho Chi Minh City",
            district_type="suburban",
            is_active=True
        )
        
        # Create test stores with different characteristics
        self.store1 = Store.objects.create(
            name="Circle K Downtown",
            address="123 Nguyen Hue, District 1",
            phone="028-1234567",
            email="store1@example.com",
            location=Point(106.7, 10.8, srid=4326),  # HCM City center
            store_type="convenience",
            district="District 1",
            district_obj=self.district1,
            city="Ho Chi Minh City",
            opening_hours="24/7",
            is_active=True,
            rating=Decimal('4.5')
        )
        
        self.store2 = Store.objects.create(
            name="FamilyMart Saigon",
            address="456 Le Lai, District 1",
            phone="028-2345678",
            email="store2@example.com",
            location=Point(106.68, 10.77, srid=4326),  # Close to center
            store_type="convenience",
            district="District 1",
            district_obj=self.district1,
            city="Ho Chi Minh City",
            opening_hours="6:00-23:00",
            is_active=True,
            rating=Decimal('4.2')
        )
        
        self.store3 = Store.objects.create(
            name="Pharmacy Plus",
            address="789 Vo Van Tan, District 3",
            phone="028-3456789",
            email="store3@example.com",
            location=Point(106.67, 10.75, srid=4326),  # Different district
            store_type="pharmacy",
            district="District 3",
            district_obj=self.district2,
            city="Ho Chi Minh City",
            opening_hours="8:00-22:00",
            is_active=True,
            rating=Decimal('4.0')
        )
        
        self.store4 = Store.objects.create(
            name="Inactive Store",
            address="999 Test Street, District 1",
            phone="028-9999999",
            email="inactive@example.com",
            location=Point(106.72, 10.82, srid=4326),
            store_type="convenience",
            district="District 1",
            district_obj=self.district1,
            city="Ho Chi Minh City",
            opening_hours="9:00-21:00",
            is_active=False,  # Inactive store
            rating=Decimal('3.0')
        )
        
        # Create test inventory items
        self.inventory1 = Inventory.objects.create(
            store=self.store1,
            item_name="Coca Cola",
            quantity=100,
            unit="pieces",
            price=Decimal('15000'),
            category="beverages",
            is_available=True
        )
        
        self.inventory2 = Inventory.objects.create(
            store=self.store1,
            item_name="Instant Noodles",
            quantity=50,
            unit="packs",
            price=Decimal('25000'),
            category="snacks",
            is_available=True
        )
        
        self.inventory3 = Inventory.objects.create(
            store=self.store2,
            item_name="Mineral Water",
            quantity=200,
            unit="bottles",
            price=Decimal('8000'),
            category="beverages",
            is_available=True
        )
        
        self.inventory4 = Inventory.objects.create(
            store=self.store3,
            item_name="Pain Relief Medicine",
            quantity=30,
            unit="boxes",
            price=Decimal('45000'),
            category="personal_care",
            is_available=True
        )
        
        # Inventory for inactive store (should not appear in results)
        self.inventory5 = Inventory.objects.create(
            store=self.store4,
            item_name="Test Item",
            quantity=10,
            unit="pieces",
            price=Decimal('10000'),
            category="other",
            is_available=True
        )
        
        # Base URL for search
        self.search_url = reverse('stores:store-search')

    def test_basic_text_search(self):
        """Test basic text search functionality."""
        response = self.client.get(self.search_url, {
            'search': 'Circle'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Circle K Downtown')

    def test_search_by_district_id(self):
        """Test filtering by district ID."""
        response = self.client.get(self.search_url, {
            'district': str(self.district1.id)
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 3 stores (2 active + 1 inactive in District 1)
        self.assertEqual(len(response.data['results']), 3)
        
        # Verify all stores are from District 1
        for store in response.data['results']:
            self.assertEqual(store['district'], 'District 1')

    def test_search_by_district_name(self):
        """Test filtering by district name."""
        response = self.client.get(self.search_url, {
            'district': 'District 3'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Pharmacy Plus')

    def test_filter_by_store_type(self):
        """Test filtering by store type."""
        response = self.client.get(self.search_url, {
            'store_type': 'convenience'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 3 convenience stores (2 active + 1 inactive)
        self.assertEqual(len(response.data['results']), 3)
        
        for store in response.data['results']:
            self.assertEqual(store['store_type'], 'convenience')

    def test_filter_by_active_status(self):
        """Test filtering by active status."""
        # Test active stores only
        response = self.client.get(self.search_url, {
            'is_active': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # 3 active stores
        
        for store in response.data['results']:
            self.assertTrue(store['is_active'])
        
        # Test inactive stores only
        response = self.client.get(self.search_url, {
            'is_active': 'false'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # 1 inactive store
        self.assertFalse(response.data['results'][0]['is_active'])

    def test_filter_by_inventory_availability(self):
        """Test filtering stores by specific inventory items."""
        # Test searching for stores with Coca Cola
        response = self.client.get(self.search_url, {
            'inventory_item': 'Coca'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return stores that have Coca Cola (partial match)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Circle K Downtown')
        
        # Test searching for stores with beverages category items
        response = self.client.get(self.search_url, {
            'inventory_item': 'Water'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return stores that have Mineral Water
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'FamilyMart Saigon')

    def test_location_based_search(self):
        """Test location-based search with radius."""
        # Search within 5km of HCM City center
        response = self.client.get(self.search_url, {
            'latitude': '10.8',
            'longitude': '106.7',
            'radius_km': '5',
            'sort_by_distance': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # Results should be sorted by distance (closest first)
        if len(response.data['results']) > 1:
            # First result should be store1 (exact location match)
            self.assertEqual(response.data['results'][0]['name'], 'Circle K Downtown')

    def test_combined_search_filters(self):
        """Test combining multiple search filters."""
        response = self.client.get(self.search_url, {
            'search': 'Circle',
            'district': str(self.district1.id),
            'store_type': 'convenience',
            'is_active': 'true',
            'inventory_item': 'Coca Cola'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        store = response.data['results'][0]
        self.assertEqual(store['name'], 'Circle K Downtown')
        self.assertEqual(store['store_type'], 'convenience')
        self.assertTrue(store['is_active'])

    def test_location_search_with_filters(self):
        """Test location-based search combined with other filters."""
        response = self.client.get(self.search_url, {
            'latitude': '10.8',
            'longitude': '106.7',
            'radius_km': '10',
            'store_type': 'convenience',
            'is_active': 'true',
            'sort_by_distance': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return only active convenience stores within radius
        for store in response.data['results']:
            self.assertEqual(store['store_type'], 'convenience')
            self.assertTrue(store['is_active'])



    def test_invalid_location_parameters(self):
        """Test error handling for invalid location parameters."""
        response = self.client.get(self.search_url, {
            'latitude': 'invalid',
            'longitude': '106.7',
            'radius_km': '5'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_search_metadata_in_response(self):
        """Test that search metadata is included in response."""
        response = self.client.get(self.search_url, {
            'search': 'test',
            'store_type': 'convenience',
            'is_active': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('search_metadata', response.data)
        
        metadata = response.data['search_metadata']
        self.assertEqual(metadata['search_text'], 'test')
        self.assertEqual(metadata['filters_applied']['store_type'], 'convenience')
        self.assertEqual(metadata['filters_applied']['is_active'], 'true')

    def test_pagination(self):
        """Test pagination in advanced search."""
        response = self.client.get(self.search_url, {
            'page': '1'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return paginated results structure
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Verify we have the expected number of stores
        self.assertEqual(response.data['count'], 4)  # 3 active + 1 inactive store from setUp

    def test_empty_search_results(self):
        """Test handling of searches with no results."""
        response = self.client.get(self.search_url, {
            'search': 'nonexistent store name'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)

    def test_case_insensitive_search(self):
        """Test that text search is case insensitive."""
        # Test lowercase
        response = self.client.get(self.search_url, {
            'search': 'circle'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test uppercase
        response = self.client.get(self.search_url, {
            'search': 'CIRCLE'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_address_search(self):
        """Test searching by address."""
        response = self.client.get(self.search_url, {
            'search': 'Nguyen Hue'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Circle K Downtown')

    def test_distance_calculation(self):
        """Test that distance is calculated correctly for location-based search."""
        response = self.client.get(self.search_url, {
            'latitude': '10.8',
            'longitude': '106.7',
            'radius_km': '10',
            'sort_by_distance': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that results are sorted by distance
        distances = []
        for store in response.data['results']:
            # Distance should be calculable from coordinates
            if 'distance' in store:
                distances.append(store['distance'])
        
        # If we have distances, they should be sorted
        if len(distances) > 1:
            self.assertEqual(distances, sorted(distances))

    def test_inventory_item_filter(self):
        """Test filtering for stores by specific inventory item."""
        # Create a store with no inventory
        store_no_inventory = Store.objects.create(
            name="Empty Store",
            address="Empty Street",
            location=Point(106.69, 10.79, srid=4326),
            store_type="convenience",
            district="District 1",
            district_obj=self.district1,
            city="Ho Chi Minh City",
            is_active=True
        )
        
        # Test filtering by specific inventory item
        response = self.client.get(self.search_url, {
            'inventory_item': 'Coca Cola'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store_names = [store['name'] for store in response.data['results']]
        # Should only include stores with Coca Cola
        self.assertIn('Circle K Downtown', store_names)
        self.assertNotIn('Empty Store', store_names)
        self.assertNotIn('FamilyMart Saigon', store_names)  # Doesn't have Coca Cola
        
        # Test filtering by another item
        response = self.client.get(self.search_url, {
            'inventory_item': 'Mineral Water'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store_names = [store['name'] for store in response.data['results']]
        # Should only include stores with Mineral Water
        self.assertIn('FamilyMart Saigon', store_names)
        self.assertNotIn('Empty Store', store_names)
        self.assertNotIn('Circle K Downtown', store_names)  # Doesn't have Mineral Water
        
        # Test that all stores are included when inventory_item is not specified
        response = self.client.get(self.search_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store_names = [store['name'] for store in response.data['results']]
        self.assertIn('Empty Store', store_names)

    def test_multiple_store_types(self):
        """Test that different store types are properly filtered."""
        # Test pharmacy type
        response = self.client.get(self.search_url, {
            'store_type': 'pharmacy'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Pharmacy Plus')
        self.assertEqual(response.data['results'][0]['store_type'], 'pharmacy')

    def test_radius_boundary(self):
        """Test that radius filtering works correctly at boundaries."""
        # Test very small radius - should return only exact matches
        response = self.client.get(self.search_url, {
            'latitude': '10.8',
            'longitude': '106.7',
            'radius_km': '0.1',  # Very small radius
            'sort_by_distance': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return at least the exact match (store1)
        self.assertGreaterEqual(len(response.data['results']), 1)
        if len(response.data['results']) >= 1:
            self.assertEqual(response.data['results'][0]['name'], 'Circle K Downtown')

    def test_automatic_distance_sorting_without_radius(self):
        """Test automatic distance sorting when location is provided without radius."""
        response = self.client.get(self.search_url, {
            'latitude': '10.8',
            'longitude': '106.7',
            'sort_by_distance': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return all stores sorted by distance
        self.assertEqual(len(response.data['results']), 4)  # All stores should be returned
        
        # First result should be the closest (store1 with exact coordinates)
        self.assertEqual(response.data['results'][0]['name'], 'Circle K Downtown')

    def test_nearby_search_without_radius_parameter(self):
        """Test that location-based search works without requiring radius parameter."""
        response = self.client.get(self.search_url, {
            'latitude': '10.8',
            'longitude': '106.7',
            'sort_by_distance': 'true',
            'is_active': 'true'  # Also test with additional filters
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return active stores sorted by distance
        self.assertEqual(len(response.data['results']), 3)  # 3 active stores
        
        # Results should be sorted by distance
        for store in response.data['results']:
            self.assertTrue(store['is_active']) 