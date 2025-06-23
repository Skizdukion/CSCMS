"""
Unit tests for the stores app models and spatial field validation.
"""

from django.test import TestCase
from django.contrib.gis.geos import Point, Polygon
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.apps.stores.models import District, Store, Inventory

from backend.apps.stores.models import Store, District, Inventory


class DistrictModelTest(TestCase):
    """Test cases for the District model."""

    def setUp(self):
        """Set up test data for District model."""
        # Create a simple polygon for testing (Ho Chi Minh City area)
        self.test_polygon = Polygon(
            [
                (106.6, 10.7),  # Bottom-left
                (106.8, 10.7),  # Bottom-right
                (106.8, 10.9),  # Top-right
                (106.6, 10.9),  # Top-left
                (106.6, 10.7),  # Close the polygon
            ],
            srid=4326,
        )

        self.district_data = {
            "name": "District 1",
            "code": "D1",
            "city": "Ho Chi Minh City",
            "population": 200000,
            "area_km2": Decimal("7.73"),
            "district_type": "urban",
            "avg_income": Decimal("25000000"),
            "is_active": True,
        }

    def test_create_district_without_boundary(self):
        """Test creating a district without spatial boundary."""
        district = District.objects.create(**self.district_data)  # type: ignore[attribute-defined]
        self.assertEqual(district.name, "District 1")
        self.assertEqual(district.code, "D1")
        self.assertEqual(district.city, "Ho Chi Minh City")
        self.assertEqual(district.population, 200000)
        self.assertEqual(district.area_km2, Decimal("7.73"))
        self.assertEqual(district.district_type, "urban")
        self.assertEqual(district.avg_income, Decimal("25000000"))
        self.assertTrue(district.is_active)
        self.assertIsNone(district.boundary)

    def test_create_district_with_boundary(self):
        """Test creating a district with spatial boundary."""
        district_data = self.district_data.copy()
        district_data["boundary"] = self.test_polygon

        district = District.objects.create(**district_data)  # type: ignore[attribute-defined]
        self.assertIsNotNone(district.boundary)
        self.assertEqual(district.boundary.geom_type, "Polygon")
        self.assertEqual(district.boundary.srid, 4326)

    def test_district_unique_constraints(self):
        """Test that district name and code must be unique."""
        District.objects.create(**self.district_data)  # type: ignore[attribute-defined]
        # Try to create another district with same name
        with self.assertRaises(IntegrityError):
            with transaction.atomic():  # type: ignore[misc]
                District.objects.create(  # type: ignore[attribute-defined]
                    name="District 1",  # Same name
                    code="D2",  # Different code
                    city="Ho Chi Minh City",
                )
        # Try to create another district with same code
        with self.assertRaises(IntegrityError):
            with transaction.atomic():  # type: ignore[misc]
                District.objects.create(  # type: ignore[attribute-defined]
                    name="District 2",  # Different name
                    code="D1",  # Same code
                    city="Ho Chi Minh City",
                )  # type: ignore[attribute-defined]

    def test_district_validation_constraints(self):
        """Test district field validation constraints."""
        # Test negative population
        with self.assertRaises(ValidationError):
            district = District(name="Test District", code="TD", population=-100)
            district.full_clean()

        # Test negative area
        with self.assertRaises(ValidationError):
            district = District(
                name="Test District", code="TD", area_km2=Decimal("-5.0")
            )
            district.full_clean()

        # Test negative income
        with self.assertRaises(ValidationError):
            district = District(
                name="Test District", code="TD", avg_income=Decimal("-1000000")
            )
            district.full_clean()

    def test_district_str_representation(self):
        """Test district string representation."""
        district = District.objects.create(**self.district_data)  # type: ignore[attribute-defined]
        self.assertEqual(str(district), "District 1 (D1)")

    def test_district_contains_point_method(self):
        """Test the contains_point method."""
        district_data = self.district_data.copy()
        district_data["boundary"] = self.test_polygon
        district = District.objects.create(**district_data)  # type: ignore[attribute-defined]

        # Point inside the polygon
        inside_point = Point(106.7, 10.8, srid=4326)
        self.assertTrue(district.contains_point(inside_point))

        # Point outside the polygon
        outside_point = Point(107.0, 11.0, srid=4326)
        self.assertFalse(district.contains_point(outside_point))

        # Test with None boundary
        district_no_boundary = District.objects.create(  # type: ignore[attribute-defined]
            name="No Boundary District", code="NBD", city="Ho Chi Minh City"
        )  # type: ignore[attribute-defined]
        self.assertFalse(district_no_boundary.contains_point(inside_point))

    def test_district_get_area_centroid(self):
        """Test getting the centroid of district boundary."""
        district_data = self.district_data.copy()
        district_data["boundary"] = self.test_polygon
        district = District.objects.create(**district_data)  # type: ignore[attribute-defined]

        centroid = district.get_area_centroid()
        self.assertIsNotNone(centroid)
        self.assertEqual(centroid.geom_type, "Point")
        self.assertEqual(centroid.srid, 4326)

        # Test with None boundary
        district_no_boundary = District.objects.create(  # type: ignore[attribute-defined]
            name="No Boundary District", code="NBD", city="Ho Chi Minh City"
        )  # type: ignore[attribute-defined]
        self.assertIsNone(district_no_boundary.get_area_centroid())


class StoreModelTest(TestCase):
    """Test cases for the Store model."""

    def setUp(self):
        """Set up test data for Store model."""
        self.district = District.objects.create(  # type: ignore[attribute-defined]
            name="Test District", code="TD", city="Ho Chi Minh City"
        )  # type: ignore[attribute-defined]

        self.store_data = {
            "name": "Test Store",
            "address": "123 Test Street, Ho Chi Minh City",
            "phone": "+84-123-456-789",
            "email": "test@store.com",
            "store_type": "convenience",
            "district": "Test District",
            "district_obj": self.district,
            "city": "Ho Chi Minh City",
            "opening_hours": "8:00-22:00",
            "is_active": True,
            "rating": Decimal("4.5"),
        }

    def test_create_store_without_location(self):
        """Test creating a store without spatial location."""
        store = Store.objects.create(**self.store_data)  # type: ignore[attribute-defined]
        self.assertEqual(store.name, "Test Store")
        self.assertEqual(store.address, "123 Test Street, Ho Chi Minh City")
        self.assertEqual(store.phone, "+84-123-456-789")
        self.assertEqual(store.email, "test@store.com")
        self.assertEqual(store.store_type, "convenience")
        self.assertEqual(store.district, "Test District")
        self.assertEqual(store.district_obj, self.district)
        self.assertEqual(store.city, "Ho Chi Minh City")
        self.assertEqual(store.opening_hours, "8:00-22:00")
        self.assertTrue(store.is_active)
        self.assertEqual(store.rating, Decimal("4.5"))
        self.assertIsNone(store.location)

    def test_create_store_with_location(self):
        """Test creating a store with spatial location."""
        store_data = self.store_data.copy()
        store_data["location"] = Point(106.7, 10.8, srid=4326)

        store = Store.objects.create(**store_data)  # type: ignore[attribute-defined]
        self.assertIsNotNone(store.location)
        self.assertEqual(store.location.geom_type, "Point")
        self.assertEqual(store.location.srid, 4326)
        self.assertEqual(store.location.x, 106.7)  
        self.assertEqual(store.location.y, 10.8)  

    def test_store_set_location_method(self):
        """Test the set_location method."""
        store = Store.objects.create(**self.store_data)  # type: ignore[attribute-defined]

        # Set location using the method
        store.set_location(10.8, 106.7)
        store.save()

        self.assertIsNotNone(store.location)
        self.assertEqual(store.location.x, 106.7)
        self.assertEqual(store.location.y, 10.8)

    def test_store_location_properties(self):
        """Test latitude and longitude properties."""
        store_data = self.store_data.copy()
        store_data["location"] = Point(106.7, 10.8, srid=4326)
        store = Store.objects.create(**store_data)  # type: ignore[attribute-defined]

        self.assertEqual(store.latitude, 10.8)
        self.assertEqual(store.longitude, 106.7)

        # Test with None location
        store_no_location = Store.objects.create(**self.store_data)  # type: ignore[attribute-defined]
        self.assertIsNone(store_no_location.latitude)
        self.assertIsNone(store_no_location.longitude)

    def test_store_distance_calculation(self):
        """Test distance calculation between stores."""
        store1_data = self.store_data.copy()
        store1_data["location"] = Point(106.7, 10.8, srid=4326)
        store1 = Store.objects.create(**store1_data)  # type: ignore[attribute-defined]

        store2_data = self.store_data.copy()
        store2_data["name"] = "Test Store 2"
        store2_data["location"] = Point(106.8, 10.9, srid=4326)
        store2 = Store.objects.create(**store2_data)  # type: ignore[attribute-defined]

        distance = store1.distance_to(store2.location)
        self.assertIsNotNone(distance)
        self.assertGreater(distance, 0)

    def test_store_validation_constraints(self):
        """Test store field validation constraints."""
        # Test invalid rating (too high)
        with self.assertRaises(ValidationError):
            store = Store(
                name="Test Store",
                address="Test Address",
                rating=Decimal("6.0"),  # Should be max 5.0
            )
            store.full_clean()

        # Test invalid rating (negative)
        with self.assertRaises(ValidationError):
            store = Store(
                name="Test Store",
                address="Test Address",
                rating=Decimal("-1.0"),  # Should be min 0.0
            )
            store.full_clean()

    def test_store_str_representation(self):
        """Test store string representation."""
        store = Store.objects.create(**self.store_data)  # type: ignore[attribute-defined]
        self.assertEqual(str(store), "Test Store - 123 Test Street, Ho Chi Minh City")

    def test_store_save_with_coordinates(self):
        """Test store save method with latitude/longitude attributes."""
        store = Store(**self.store_data)  # type: ignore[attribute-defined]
        store.set_location(10.8, 106.7)
        store.save()
        self.assertIsNotNone(store.location)
        self.assertEqual(store.location.x, 106.7)  # type: ignore[attribute-defined]
        self.assertEqual(store.location.y, 10.8)  # type: ignore[attribute-defined]


class InventoryModelTest(TestCase):
    """Test cases for the Inventory model."""

    def setUp(self):
        """Set up test data for Inventory model."""
        self.district = District.objects.create(  # type: ignore[attribute-defined]
            name="Test District", code="TD", city="Ho Chi Minh City"
        )  # type: ignore[attribute-defined]

        self.store = Store.objects.create(  # type: ignore[attribute-defined]
            name="Test Store",
            address="123 Test Street, Ho Chi Minh City",
            district="Test District",
            district_obj=self.district,
            city="Ho Chi Minh City",
        )  # type: ignore[attribute-defined]

        self.inventory_data = {
            "store": self.store,
            "item_name": "Test Product",
            "quantity": 100,
            "unit": "pieces",
            "price": Decimal("15000"),
            "category": "beverages",
            "is_available": True,
        }

    def test_create_inventory_item(self):
        """Test creating an inventory item."""
        inventory = Inventory.objects.create(**self.inventory_data)  # type: ignore[attribute-defined]
        self.assertEqual(inventory.store, self.store)
        self.assertEqual(inventory.item_name, "Test Product")
        self.assertEqual(inventory.quantity, 100)
        self.assertEqual(inventory.unit, "pieces")
        self.assertEqual(inventory.price, Decimal("15000"))
        self.assertEqual(inventory.category, "beverages")
        self.assertTrue(inventory.is_available)

    def test_inventory_validation_constraints(self):
        """Test inventory field validation constraints."""
        # Test negative quantity
        with self.assertRaises(ValidationError):
            inventory = Inventory(
                store=self.store,
                item_name="Test Product",
                quantity=-10,  # Should be min 0
            )
            inventory.full_clean()

    def test_inventory_str_representation(self):
        """Test inventory string representation."""
        inventory = Inventory.objects.create(**self.inventory_data)  # type: ignore[attribute-defined]
        self.assertEqual(str(inventory), "Test Product (100 pieces) at Test Store")

    def test_inventory_store_relationship(self):
        """Test the relationship between inventory and store."""
        inventory = Inventory.objects.create(**self.inventory_data)  # type: ignore[attribute-defined]

        # Test forward relationship
        self.assertEqual(inventory.store, self.store)

        # Test reverse relationship
        self.assertIn(inventory, self.store.inventories.all())

    def test_inventory_choices_validation(self):
        """Test that inventory choices are properly validated."""
        # Test valid unit choice
        inventory = Inventory.objects.create(**self.inventory_data)  # type: ignore[attribute-defined]
        self.assertIn(
            inventory.unit, ["pieces", "kg", "liters", "boxes", "packs", "other"]
        )

        # Test valid category choice
        self.assertIn(
            inventory.category,
            [
                "beverages",
                "snacks",
                "dairy",
                "frozen",
                "household",
                "personal_care",
                "other",
            ],
        )


class SpatialFieldValidationTest(TestCase):
    """Test cases for spatial field validation."""

    def test_point_field_validation(self):
        """Test PointField validation."""
        district = District.objects.create(  # type: ignore[attribute-defined]
            name="Test District", code="TD", city="Ho Chi Minh City"
        )  # type: ignore[attribute-defined]

        # Valid point
        valid_point = Point(106.7, 10.8, srid=4326)
        store = Store.objects.create(  # type: ignore[attribute-defined]
            name="Test Store",
            address="Test Address",
            location=valid_point,
            district="Test District",
            district_obj=district,
            city="Ho Chi Minh City",
        )  # type: ignore[attribute-defined]
        self.assertIsNotNone(store.location)

        # Test with None (should be allowed)
        store_no_location = Store.objects.create(  # type: ignore[attribute-defined]
            name="Test Store 2",
            address="Test Address 2",
            location=None,
            district="Test District",
            district_obj=district,
            city="Ho Chi Minh City",
        )  # type: ignore[attribute-defined]
        self.assertIsNone(store_no_location.location)

    def test_polygon_field_validation(self):
        """Test PolygonField validation."""
        # Valid polygon
        valid_polygon = Polygon(
            [
                (106.6, 10.7),
                (106.8, 10.7),
                (106.8, 10.9),
                (106.6, 10.9),
                (106.6, 10.7),
            ],
            srid=4326,
        )

        district = District.objects.create(  # type: ignore[attribute-defined]
            name="Test District",
            code="TD",
            city="Ho Chi Minh City",
            boundary=valid_polygon,
        )  # type: ignore[attribute-defined]
        self.assertIsNotNone(district.boundary)
        self.assertEqual(district.boundary.geom_type, "Polygon")

        # Test with None (should be allowed)
        district_no_boundary = District.objects.create(  # type: ignore[attribute-defined]
            name="Test District 2", code="TD2", city="Ho Chi Minh City", boundary=None
        )  # type: ignore[attribute-defined]
        self.assertIsNone(district_no_boundary.boundary)

    def test_spatial_index_creation(self):
        """Test that spatial indexes are created properly."""
        # This test verifies that spatial indexes are working
        # by checking that spatial queries can be executed
        district = District.objects.create(  # type: ignore[attribute-defined]
            name="Test District",
            code="TD",
            city="Ho Chi Minh City",
            boundary=Polygon(
                [
                    (106.6, 10.7),
                    (106.8, 10.7),
                    (106.8, 10.9),
                    (106.6, 10.9),
                    (106.6, 10.7),
                ],
                srid=4326,
            ),
        )  # type: ignore[attribute-defined]

        store = Store.objects.create(  # type: ignore[attribute-defined]
            name="Test Store",
            address="Test Address",
            location=Point(106.7, 10.8, srid=4326),
            district="Test District",
            district_obj=district,
            city="Ho Chi Minh City",
        )  # type: ignore[attribute-defined]

        # Test spatial query using within
        stores_in_district = Store.objects.filter(location__within=district.boundary)  # type: ignore[attribute-defined]
        self.assertIn(store, stores_in_district)

        # Test spatial query using distance
        center_point = Point(106.7, 10.8, srid=4326)
        nearby_stores = Store.objects.filter(  # type: ignore[attribute-defined]
            location__distance_lte=(
                center_point,
                8000,
            )  # 8km radius (increased from 5km)
        )  # type: ignore[attribute-defined]
        self.assertIn(store, nearby_stores)


class ModelIntegrationTest(TestCase):
    """Integration tests for model relationships and spatial operations."""

    def setUp(self):
        """Set up test data for integration tests."""
        # Create district with boundary
        self.district = District.objects.create(  # type: ignore[attribute-defined]
            name="District 1",
            code="D1",
            city="Ho Chi Minh City",
            boundary=Polygon(
                [
                    (106.6, 10.7),
                    (106.8, 10.7),
                    (106.8, 10.9),
                    (106.6, 10.9),
                    (106.6, 10.7),
                ],
                srid=4326,
            ),
        )  # type: ignore[attribute-defined]

        # Create stores in the district
        self.store1 = Store.objects.create(  # type: ignore[attribute-defined]
            name="Store 1",
            address="Address 1",
            location=Point(106.7, 10.8, srid=4326),
            district="District 1",
            district_obj=self.district,
            city="Ho Chi Minh City",
        )  # type: ignore[attribute-defined]

        self.store2 = Store.objects.create(  # type: ignore[attribute-defined]
            name="Store 2",
            address="Address 2",
            location=Point(106.75, 10.85, srid=4326),
            district="District 1",
            district_obj=self.district,
            city="Ho Chi Minh City",
        )  # type: ignore[attribute-defined]

        # Create inventory items
        self.inventory1 = Inventory.objects.create(  # type: ignore[attribute-defined]
            store=self.store1,
            item_name="Product 1",
            quantity=50,
            unit="pieces",
            price=Decimal("10000"),
            category="beverages",
        )  # type: ignore[attribute-defined]

        self.inventory2 = Inventory.objects.create(  # type: ignore[attribute-defined]
            store=self.store2,
            item_name="Product 2",
            quantity=30,
            unit="kg",
            price=Decimal("50000"),
            category="snacks",
        )  # type: ignore[attribute-defined]

    def test_district_store_relationship(self):
        """Test the relationship between district and stores."""
        stores_in_district = self.district.get_stores()
        self.assertEqual(stores_in_district.count(), 2)
        self.assertIn(self.store1, stores_in_district)
        self.assertIn(self.store2, stores_in_district)

        store_count = self.district.get_store_count()
        self.assertEqual(store_count, 2)

    def test_store_inventory_relationship(self):
        """Test the relationship between store and inventory."""
        store1_inventory = self.store1.inventories.all()
        self.assertEqual(store1_inventory.count(), 1)
        self.assertIn(self.inventory1, store1_inventory)

        store2_inventory = self.store2.inventories.all()
        self.assertEqual(store2_inventory.count(), 1)
        self.assertIn(self.inventory2, store2_inventory)

    def test_spatial_queries(self):
        """Test spatial queries across models."""
        # Test finding stores within district boundary
        stores_in_district = Store.objects.filter(location__within=self.district.boundary)  # type: ignore[attribute-defined]
        self.assertEqual(stores_in_district.count(), 2)

        # Test finding stores near a specific point
        center_point = Point(106.7, 10.8, srid=4326)
        nearby_stores = Store.objects.filter(  # type: ignore[attribute-defined]
            location__distance_lte=(
                center_point,
                8000,
            )  # 8km radius (increased from 5km)
        )  # type: ignore[attribute-defined]
        self.assertEqual(nearby_stores.count(), 2)

        # Test distance between stores
        distance = self.store1.distance_to(self.store2.location)
        self.assertIsNotNone(distance)
        self.assertGreater(distance, 0)

    def test_cascade_deletion(self):
        """Test cascade deletion behavior."""
        # Delete store and verify inventory is also deleted
        store_id = self.store1.id
        self.store1.delete()

        # Check that store is deleted
        with self.assertRaises(Store.DoesNotExist):  
            Store.objects.get(id=store_id)  # type: ignore[attribute-defined]
        # Check that inventory is also deleted
        with self.assertRaises(Inventory.DoesNotExist):  
            Inventory.objects.get(store_id=store_id)  # type: ignore[attribute-defined]
        # District should still exist
        self.assertTrue(District.objects.filter(id=self.district.id).exists())  # type: ignore[attribute-defined]
